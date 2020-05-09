#include <math.h>
// Malmo:
#include <AgentHost.h>
#include <ClientPool.h>
using namespace malmo;

// STL:
#include <cstdlib>
#include <exception>
#include <iostream>
#include <fstream>
#include <streambuf>
#include <string>
using namespace std;

  int yawN[] = { 0, 1, 2, 3, 4, 5, 6, 7, 8 };
  int yawE[] = { 2, 5, 8, 1, 4, 7, 0, 3, 6 };
  int yawS[] = { 8, 7, 6, 5, 4, 3, 2, 1, 0 };
  int yawW[] = { 6, 3, 0, 7, 4, 1, 8, 5, 2 };

  const int YAW_NORTH = 0;
  const int YAW_EAST = 1;
  const int YAW_SOUTH = 2;
  const int YAW_WEST = 3;

  int* yaws[] = { yawN, yawE, yawS, yawW };

class MalmoGame {
public:

  MalmoGame(const char* missionFilename) {

     ifstream missionFile(missionFilename);
     const string missionXML((istreambuf_iterator<char>(missionFile)),
                              istreambuf_iterator<char>());

     mission = new MissionSpec(missionXML, true);
     //missionRecord = new MissionRecordSpec("./saved_data.tgz"); 
     missionRecord = new MissionRecordSpec(); 

     for (int i = 0; i < 3; i++) {
        relativeElements[i] = new char*[NBR_SIZE];
     }

  }

  ~MalmoGame() {
      if (mission != 0) {
         delete mission;
      }
      if (missionRecord != 0) {
         delete missionRecord;
      }
     for (int i = 0; i < 3; i++) {
        if (relativeElements[i]) delete[] relativeElements[i];
     }
  }

protected:
  const char * PITCH="\"Pitch\"";
  const char * YAW="\"Yaw\""; 
  const char * ZPOS = "\"ZPos\"";
  const char * YPOS = "\"YPos\"";
  const char * XPOS = "\"XPos\"";
  const char * TIME_ALIVE="\"TimeAlive\"";
  const char * NBR3X3 = "\"nbr3x3\":[";

  string AIR = "air";
  string  DIRT = "dirt";
  string RED_FLOWER = "red_flower";
  string LAVA = "flowing_lava";
  string BEDROCK = "bedrock";
  string  LADDER = "ladder";

  int NBR_SIZE = 3 * 3 * 3;
  char** relativeElements[3];

  AgentHost agent_host; 
  MissionSpec *mission;
  MissionRecordSpec *missionRecord;
  WorldState world_state;

  bool connect() {
      int attempts = 0;
      bool connected = false;
      do {
          try {
              agent_host.startMission(*mission, *missionRecord);
              connected = true;
          }
          catch (exception& e) {
              cout << "Error starting mission: " << e.what() << endl;
              attempts += 1;
              if (attempts >= 3)
                  return false; 
              else
                  boost::this_thread::sleep(boost::posix_time::milliseconds(1000)); 
          }
      } while (!connected);
      return true;
  }

  void waitForMissionStarted() {
      cout << "Waiting for the mission to start" << flush;
      do {
          cout << "." << flush;
          boost::this_thread::sleep(boost::posix_time::milliseconds(100));
          world_state = agent_host.getWorldState();
          for( boost::shared_ptr<TimestampedString> error : world_state.errors )
              cout << "Error: " << error->text << endl;
      } while (!world_state.has_mission_begun);
      cout << endl;
  }

  float getFordulasSebessege(float yaw, float celYaw) {
     float dif = celYaw - yaw;
     float yaw2 = yaw;
     if (dif > 180 || dif < -180) {
        yaw2 -= 360;
     }
     float fordulasSebessege = (celYaw -yaw2) / 45;
     return fordulasSebessege;
  }

  virtual void missionStarted() {
  }

  virtual int getMainLoopSleepTime() {
     return 500;
  }

  void sleep(int ms) {
      boost::this_thread::sleep(boost::posix_time::milliseconds(ms));
  }

  void varakozas(int sleepTime = 0) { 
     if (sleepTime > 0) {
        sleep(sleepTime);
     }
  }

  void sendCommand(string&& command, int sleepTime = 0) {
     agent_host.sendCommand(command);
     varakozas(sleepTime);
  }

  virtual void doAction() {
  }


  void mainLoop() {
    world_state = agent_host.getWorldState();
    do {
       doAction();
       sleep(getMainLoopSleepTime());
       world_state = agent_host.getWorldState();
    } while (world_state.is_mission_running);
  }

  
  int getElementRelativePosition(const string& obs, int level, string& elem, int kezdopoz = 0) {
     int poz = -1;
     for (int i = kezdopoz; i < 3 * 3; i++) {
        if (isRelativeElement(obs, level, i, elem)) {
           poz = i;
           return poz;
        }
     } 
     return poz;
  }

  bool isRelativeElement(const string& obs, size_t level, size_t relativePos, string& elem) {
     const char * e = getRelativeElement(obs, level, relativePos);
     if (e == 0) return false;
     return strncmp(e, elem.c_str(), strlen(elem.c_str())) == 0;
  }

  const char* getRelativeElement(const string& obs, size_t level, size_t relativePos) {
     float yaw = getYaw(obs);
     int yawIndex = getYawIndex(yaw);
     int elemIndex = level * 3 * 3 + yaws[yawIndex][relativePos];
     return getNbr3x3Elem(obs, elemIndex);
  }

  int getYawIndex(float yaw) {
     if ((yaw <= 45 && yaw > -45) || yaw > 360 - 45) return YAW_SOUTH;
     if (yaw > 45 && yaw <= 90 + 45) return YAW_WEST;
     if (yaw > 180 + 45  && yaw <= 270 + 45 ) return YAW_EAST;
     return  YAW_NORTH;
  }

  int strnthpos(const char *haystack, const char *needle, int nth) {
      const char *res = haystack;
      for(int i = 1; i <= nth; i++) {
          res = strstr(res, needle);
          if (!res)
              return -1;
          else if(i != nth)
              res++;
      }
      return res - haystack;
  }

  const char* getNbr3x3Elem(const string& obs, size_t pos) {
     size_t nbrPos = obs.find(NBR3X3);
     if (nbrPos != string::npos) {
        nbrPos += strlen(NBR3X3);
        int nthPos = strnthpos(obs.c_str() + nbrPos, "\"", (pos * 2) + 1);
        if (nthPos >= 0) {
           return obs.c_str() + nthPos + nbrPos + 1;
        }
     }
     return 0;
  }

  bool isNbr3x3(const string& obs, size_t pos, const char* elem) {
     const char* s = getNbr3x3Elem(obs, pos);
     if (s != 0) {
         return strncmp(s, elem, strlen(elem)) == 0;
     }
     return false;
  }

  int getElementPos(const string& obs, string&  elem) {
     return getElementPos(obs, elem.c_str());
  }

  int getElementPos(const string& obs, const char* elem) {
      for (int i = 0; i < NBR_SIZE; i++) {
         if (isNbr3x3(obs, i, elem)) {
            return i;
         }
      }
      return -1;
  }

  int getRedFlowerPos(const string& obs) {
     return getElementPos(obs, RED_FLOWER);
  }

  int getLavaPos(const string& obs) {
     return getElementPos(obs, LAVA);
  }

  float getPitch(const string& obs) {
      return getObservationFloat(obs, PITCH); 
  }

  float getYaw(const string& obs) {
      float y = getObservationFloat(obs, YAW); 
      if (y < 0) {
         cout << "YAW negatív..." << y << endl;
         y += 360;
      }
      return y;
  }

  float getXPos(const string& obs) {
      return getObservationFloat(obs, XPOS); 
  }

  float getYPos(const string& obs) {
      return getObservationFloat(obs, YPOS); 
  }

  float getZPos(const string& obs) {
      return getObservationFloat(obs, ZPOS); 
  }


  int getObservationInt(const string& str, const char* key, int alapertek = -1) {
      size_t pos = str.find(key);
      if (pos != string::npos) {
         pos += strlen(key) + 1;
         int i = atoi(str.c_str() + pos);
         return i;
      }
      return alapertek;
  }

  float getObservationFloat(const string& str, const char* key, float alapertek = -1.0) {
      size_t pos = str.find(key);
      if (pos != string::npos) {
         pos += strlen(key) + 1;
         float i = strtof(str.c_str() + pos, NULL);
         return i;
      }
      return alapertek;
  }

public:
  int startMission() {
     bool connected = connect();
     if (connected) {

        waitForMissionStarted();

        missionStarted();
 
        mainLoop();

     } else {
        return EXIT_FAILURE;
     } 
     return 0;
  }
};
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
///// RFH4
class OZSRFH4: public MalmoGame {
public:
   OZSRFH4(string mission): MalmoGame(mission.c_str()), kellFordulni(false), aktualisAllapot(-1) {
     fordulasUtanVarakozas = false;
     yMax = 999;
     startYaw = 100000;
   }
   OZSRFH4() : MalmoGame("20200505.xml"), kellFordulni(false), aktualisAllapot(-1) {
     fordulasUtanVarakozas = false;
     yMax = 999;
     startYaw = 100000;
   }

   static const int ELORE = 1;
   static const int ELORE_FEL = 2;
   static const int FORDUL = 3;
   static const int VIRAG = 4;
   string FAL = "bedrock";

protected:

   bool kellFordulni;
   bool fordulasUtanVarakozas;
   int fordulasUtaniAllapot;
   bool kellPitchelni;
   float celPitch;
   float celYaw;
   float celY;
   int aktualisAllapot;
   float yMax;
   float startYaw;

   int getMainLoopSleepTime() {
      return 10;
   }

   void printYaw() {
      for( boost::shared_ptr<TimestampedString> observ : world_state.observations ) {
          const string& obs = observ->text;
          cout << "observation: " << obs << endl;
          float yaw = getYaw(obs);
          cout << "yaw:" << yaw << endl;
      }
   }

   void missionStarted() {
      celY = 12;
      yMax = 14; // celY + 1;
      allapotValtas(ELORE_FEL);
   }
  
   void printElottunk(const char* e) {
     for (int j = 0; e[j] != '"'; j++) {
         cout << e[j] ; 
     }
   }

   void allapotValtas(int ujAllapot) {
       cout << "Allapotvaltas: " << aktualisAllapot << " -> " << ujAllapot << endl;

       if (aktualisAllapot == ujAllapot) {
          return;
       }

       switch (aktualisAllapot) {
          case VIRAG:
             sendCommand("attack 0");
             varakozas(500);
             kellPitchelni = true;
             celPitch = 20;
          case FORDUL:
             sendCommand("turn 0", 0);
	     /*
 	     if (fordulasUtanVarakozas) {
	         varakozas(1000);
	     }
	     */
	     fordulasUtanVarakozas = false;
             break;
          case ELORE:
             sendCommand("move 0", 0);
             sendCommand("jump 0", 0);
             break;
          case ELORE_FEL:
             sendCommand("strafe 0", 0); 
             sendCommand("move 1", 1000);
             sendCommand("move 0", 10); 
             sendCommand("jump 0", 10); 
             sendCommand("use 0", 10); 
             sendCommand("hotbar.3 1", 0);
             break;
       }

       switch (ujAllapot) {
          case ELORE_FEL:
              sendCommand("hotbar.2 1", 0);
              sendCommand("use 1", 0);
              break;
          case ELORE:
              //sendCommand("move 1", 500);
              sendCommand("move 1", 0);
          case VIRAG:
              cout << "Virág!!!" << endl;
       }
       aktualisAllapot = ujAllapot;
   }

   void jobbraFordul(float yaw) {
       cout << "fordulni kell..." << yaw << " cél:" << celYaw << endl;
       kellFordulni = true;
       celYaw = yaw + 90;
       if (celYaw > 360) {
         celYaw -= 360;
       }
       float yawf = celYaw;
       yawf = round(yawf / 90.0) * 90;              
       celYaw = static_cast<int>(yawf);
       cout << "celYaw:" << celYaw << endl;
  
       allapotValtas(FORDUL);
   }

   void doAction() {

      int i = 0;
      for( boost::shared_ptr<TimestampedString> observ : world_state.observations ) {
          const string& obs = observ->text;
          if (obs.find("Zombie") != string::npos) {
             cout << i++ << ".observation: " << obs << endl;
          }

          float yaw = getYaw(obs);
          if (startYaw > 1000) {
              startYaw = yaw;
          }    
          
          float pitch = getPitch(obs);
          float y = getYPos(obs);
          float x = getXPos(obs);
          float z = getZPos(obs);
          const char* e = getRelativeElement(obs, 1, 1);
          float yawf;
          int viragPoz;
          int hatsoViragPoz = -1;
          cout << "Pitch:" << pitch << endl;

          if (kellPitchelni) {
             if (celPitch + 5 < pitch) {
                sendCommand("pitch -0.5");
             } else {
                if (celPitch > pitch + 5) {
                   sendCommand("pitch 0.5");
                } else {
                   if (celPitch < pitch - 2) {
                       sendCommand("pitch -0.5");
                   } else {
                      kellPitchelni = false;
                      celPitch = 30;
                      sendCommand("pitch 0");
                   }
                }
             } 
          }
          
          if (obs.find("Zombie") != string::npos) {
              //sendCommand("attack 0");
              //sendCommand("attack 1");
          }

          cout << "Aktualis allapot:" << aktualisAllapot << endl;
          switch (aktualisAllapot) {
             case VIRAG:
                 viragPoz = getElementRelativePosition(obs, 1, RED_FLOWER);
                 hatsoViragPoz = getElementRelativePosition(obs, 1, RED_FLOWER, 7);
                 cout << "Virág:" << viragPoz << endl;
                 cout << "Hátsó Virág:" << hatsoViragPoz << endl;
                 //cout << obs << endl;
                 if (viragPoz < 0) {
                    allapotValtas(ELORE);
                 }
                 
                 if (hatsoViragPoz == 7 || viragPoz == 6 || viragPoz == 8) {
                            sendCommand("move -0.5");
                 } else {
                    if (viragPoz == 1 || viragPoz == 2) {
                        sendCommand("move 0.5");
                    } else {
                        if (viragPoz == 5) {
                            //fordulasUtanVarakozas = true;
                            //fordulasUtaniAllapot = VIRAG;
                            //jobbraFordul(yaw);
                            sendCommand("strafe 0.2");
                            break;
                        } else {
                            if (viragPoz == 0 || viragPoz == 3) {
                               sendCommand("strafe -0.2");
                            } else {
                               sendCommand("strafe 0");
                            }
                        }
                    }
                 }
                 if (viragPoz == 4) {
                    sendCommand("move 0");
                 }
                 //cout << "Pitch:" << pitch << endl;
                 sendCommand("pitch 1", 0); 
                 sendCommand("attack 1");
                 break;
             case ELORE_FEL:
                 if (y > celY)  {
                    //cout << " y:" << y << " celY:" << celY << " yMax:" << yMax << endl;
                    //sendCommand("strafe 1", 500);
                    //sendCommand("strafe 0");
                    allapotValtas(ELORE);
                 } else {
                 
                    cout << endl;
                    if (isRelativeElement(obs, 1, 1, FAL)) {
                       if (isRelativeElement(obs, 2, 4, LADDER) ||
                           isRelativeElement(obs, 2, 1, AIR)) { 
                          cout << "jump, move" << endl;
                          sendCommand("jump 1", 100); 
                          sendCommand("move 1"); 
                       } else {
                          cout << "Nincs létra!!" << endl;
                          sendCommand("move -1"); 
                       }
                    } else {
                       cout << "move 1" << endl;
                       sendCommand("move 1", 0); 
                    }
                 }
                 
                 break;
             case ELORE:
                 
                 
                 viragPoz = getElementRelativePosition(obs, 1, RED_FLOWER);
                 if (viragPoz >= 0) {
                     allapotValtas(VIRAG); 
                     break;
                 }
                 viragPoz = getElementRelativePosition(obs, 0, RED_FLOWER);
                 if (viragPoz >= 0) {
                     cout << "Virág lent!!!" << endl;
                     sendCommand("move 0");
                     sendCommand("strafe 0.6");
                     break;
                 }
                 viragPoz = getElementRelativePosition(obs, 2, RED_FLOWER);
                 if (viragPoz >= 0) {
                     cout << "Virág fent!!!" << endl;
                     sendCommand("move 0");
                     sendCommand("strafe -1");
                     sendCommand("jump 1", 200);
                     sendCommand("jump 0");
                     break;
                 }

                 if (isRelativeElement(obs, 1, 1, FAL)) {
                   cout << "Fal elöttünk..." << endl;
                   if (isRelativeElement(obs, 2, 1, AIR)) {
		              if (isRelativeElement(obs, 1, 7, FAL) ||  y  < yMax) {
                         cout << "lehet ugrani..." << endl;
                         sendCommand("jump 1", 200); 
                         sendCommand("jump 0", 0);
                         break; 
                      }
                   }
                   fordulasUtaniAllapot = ELORE;
                   jobbraFordul(yaw); 
                 } else { 
                   cout << "elore:   yaw:" << yaw << " x:" << x << " y:" << y << " z:" << z << endl;
                   yawf = yaw;
                   yawf = round(yawf / 90.0) * 90;              
                   float fordulasSebessege = getFordulasSebessege(yaw, yawf);
                    ostringstream oss2;
                    oss2 << "turn " << fordulasSebessege; 
                    cout << "A fordulas:" << oss2.str() << endl;
                    sendCommand(oss2.str(), 0);
                    if (yMax > y + 3) {
                        yMax = y + 3;
                    }
                    if (isRelativeElement(obs, 1, 1, LADDER) || isRelativeElement(obs, 2, 1, LADDER)) {
                       cout << "Létra!!! " /*<< yMax*/ << endl;
                       //cout << obs << endl;
                       sendCommand("strafe 0.2");
                       if (yaw != startYaw) {
                          yMax = y - 2;
                       }
                    } else {
                      if (y <= yMax) {
                          if (isRelativeElement(obs, 0, 4, AIR)) {
                              sendCommand("strafe -1");
                          } else {
                              sendCommand("strafe 0");
                          }
                      } else {
                         sendCommand("move 0.5", 100);  
                         sendCommand("strafe 0.4");
                      }
                    }
                    if (obs.find("Zombie") != string::npos) {
                       float distance = getObservationFloat(obs, "\"distance\"");
                       cout << "distance:" << distance << endl;
                       if (distance < 2.5 && 1 != 2) {
                          //sendCommand("move -0.2", 0);
                           sendCommand("attack 0");
                           sendCommand("attack 1");
                       } else {
                          sendCommand("move 1", 0);
                       }
                    } else {
                        sendCommand("move 1", 0);
                    }
                    //sendCommand("sprint 1", 0);
                 }
                 break;
              case FORDUL:
                 if (yaw + 360 - celYaw < 20) {
                     yaw += 360;
                 }
                 float dif = celYaw - yaw;
                 if (dif < 2 && dif > -1) {
                    cout << "rendben a fordulas, nem kell tovabb.." << yaw << "   " << celYaw << endl;
                    kellFordulni = false;
                    allapotValtas(ELORE);
                 } else {
                    //float yaw2 = yaw;
                    //if (dif > 180 || dif < -180) {
                    //  yaw2 -= 360;
                    //}
                    //float fordulasSebessege = (celYaw -yaw2) / 45;
                    float fordulasSebessege = getFordulasSebessege(yaw, celYaw);
                    cout << "fordulas..." << yaw << " -> " << celYaw << " " << fordulasSebessege << endl; 
                    ostringstream oss;
                    oss << "turn " << fordulasSebessege; 
                    cout << "A fordulas:" << oss.str() << endl;
                    sendCommand(oss.str(), 0);
                 }
                 break;
          }
 
      }
   }

};

int main(int argc, char** argv) {
   string mission;
   if (argc < 2) {
       mission = "nb4tf4i_d4_Rudolf_hard.xml";     
   } else {
       mission = argv[1];
   }
   OZSRFH4 t(mission);
   t.startMission(); 
}
