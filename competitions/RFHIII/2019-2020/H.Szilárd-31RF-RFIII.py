from __future__ import print_function
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #2: Run simple mission using raw XML

# Added modifications by Norbert Bátfai (nb4tf4i) batfai.norbert@inf.unideb.hu, mine.ly/nb4tf4i.1
# 2018.10.18, https://bhaxor.blog.hu/2018/10/18/malmo_minecraft
# 2020.02.02, NB4tf4i's Red Flowers, http://smartcity.inf.unideb.hu/~norbi/NB4tf4iRedFlowerHell


from builtins import range
import MalmoPython
import os
import sys
import time
import random
import json
import math

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

# -- set up the mission -- #
missionXML_file='nb4tf4i_d_2.xml'
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")    
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")    
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.drawBlock( 0, 0, 0, "lava")


class Hourglass:
    def __init__(self, charSet):
        self.charSet = charSet
        self.index = 0
    def cursor(self):
        self.index=(self.index+1)%len(self.charSet)
        return self.charSet[self.index]

hg = Hourglass('|/-\|')

class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.x = 0
        self.y = 0
        self.z = 0        
        self.yaw = 0
        self.pitch = 0 
    
    #def kiszed(self,nbr):
        #self
    def isInTrap(self, nbr3x3x3):
        dc = 0    
        nbri = [9,10,11,12,14,15,16,17]    
        for i in range(0, len(nbri)):
            if nbr3x3x3[nbri[i]]=="dirt" :
                dc = dc + 1            
        return dc > 5

    def run(self):
        world_state = self.agent_host.getWorldState()
        lepes=0
        kezd=0
        uthossz=3
        sz=108
        kor=0
        ford=0
        virag=0
        nemfordult=0
        elso=0
        lepesek=0
        fentkiszedve=False
        lentkiszedve=False

        fordnorth=False
        fordsouth=False
        fordeast=False
        fordwest=False


        # Loop until mission ends:
        while world_state.is_mission_running:
            #print("--- nb4tf4i arena -----------------------------------\n")
            while(lepesek<=34):
                self.agent_host.sendCommand("jumpmove 1")
                time.sleep(0.01);
                self.agent_host.sendCommand("move 1")
                time.sleep(0.01);
                print(lepesek,'\n')
                lepesek=lepesek+1
                if lepesek == 35:
                    fent=True
                    print("Fent:",fent)
            if fent == True :
                fent = False
                self.agent_host.sendCommand("move -1")
                time.sleep(.1)
                self.agent_host.sendCommand("turn 1")
                time.sleep(.1)

            if world_state.number_of_observations_since_last_state != 0:
                
                sensations = world_state.observations[-1].text
                #print("    sensations: ", sensations)                
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)
                #print("    3x3x3 neighborhood of Steve: ", nbr3x3x3)
                
                if "Yaw" in observations:
                    self.yaw = int(observations["Yaw"])
                if "Pitch" in observations:
                    self.pitch = int(observations["Pitch"])
                if "XPos" in observations:
                    self.x = int(observations["XPos"])
                if "ZPos" in observations:
                    self.z = int(observations["ZPos"])        
                if "YPos" in observations:
                    self.y = int(observations["YPos"])  
                
               # print("    Steve's Coords: ", self.x, self.y, self.z)        
               # print("    Steve's Yaw: ", self.yaw)        
               # print("    Steve's Pitch: ", self.pitch)

                if "LineOfSight" in observations:   
                    lineOfSight = observations["LineOfSight"]
                    self.lookingat = lineOfSight["type"]
                #if "LineOfSight" in observations:
                    #hotbar_0_item=observations["Hotbar_0_item"]
                    #self.=nbr3x3["type"]
                #print("    Steve's <): ", self.lookingat)
                #if self.lookingat == "red_flower":
                   # print("Viragot eszleltem!\n") 

                   # self.agent_host.sendCommand("attack 1")
                   # time.sleep(.2)
                   # virag=1
                   # self.agent_host.sendCommand("strafe 1")
                  #  time.sleep(.1)
                  #  sz=sz-4
                  #  kor=0
                 #   virag=0
               # elif nbr3x3x3[13]=='red_flower':
                   # print("Virag alattam!\n") 

                  #  time.sleep(0.2) 
                  #  self.agent_host.sendCommand("attack 1")
                 #   time.sleep(0.2)
                #    virag=1
                  #  self.agent_host.sendCommand("stafe 1")
                  #  time.sleep(.1)
                 #   sz=sz-4
                 #   kor=0
                 #   virag=0
                if nbr3x3x3[13]=='red_flower':
                    print("Virag alattam!\n") 
                    if self.yaw==0:
                        fordsouth=True
                    if self.yaw==90:
                        fordwest=True
                    if self.yaw==180:
                        fordnorth=True
                    if self.yaw==270:
                        fordeast=True
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(0.4)
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("turn 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("move 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("move 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.1)
                    #self.agent_host.sendCommand("strafe 1")
                    #time.sleep(.1)
                    virag=virag+1
                    print("virag:",virag)
                    fentkiszedve=True
                    if self.yaw==0:
                        kor=kor+1
                        print("kor:",kor)
                        fordsouth=True
                        print("Southot neztem fordultam jobbra")
                    elif self.yaw==90:
                        kor=kor+1
                        print("kor:",kor)
                        fordwest=True
                        print("Westet neztem fordultam jobbra")
                    elif self.yaw==180:
                        kor=kor+1
                        print("kor:",kor)
                        fordnorth=True
                        print("Northot neztem fordultam jobbra")
                    elif self.yaw==270:
                        kor=kor+1
                        print("kor:",kor)
                        fordeast=True
                        print("Eastet neztem fordultam jobbra")
                #FOLD
                if kor==4:
                    kor=0
                    print("kor:",kor)
                    fordnorth=False
                    fordeast=False
                    fordwest=False
                    fordsouth=False

                if self.yaw==0 and nbr3x3x3[16]=='dirt' and fordsouth==False:
                   # if nbr3x3x3[14]=='red_flower':
                     #   print("Sarokban toleb balra virag")
                     #   self.agent_host.sendCommand("strafe -1")
                      #  self.agent_host.sendCommand("attack 1")
                      #  self.agent_host.sendCommand("jumpstrafe 1")
                      #  self.agent_host.sendCommand("turn 1")
                      #  self.agent_host.sendCommand("move 1")
                      #  self.agent_host.sendCommand("strafe 1")
                      #  self.agent_host.sendCommand("strafe 1")
                      #  kor=kor+1
                      #  print("kor:",kor)
                   # else:
                        print("Southot nezem fordulok jobbra")
                        self.agent_host.sendCommand("turn 1")
                        time.sleep(.2)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.2)
                        fordsouth=True
                        kor=kor+1
                        print("kor:",kor)
                elif self.yaw==90 and nbr3x3x3[12]=='dirt' and fordwest==False:
                   # if nbr3x3x3[16]=='red_flower':
                      #  print("Sarokban toleb balra virag")
                      #  self.agent_host.sendCommand("strafe -1")
                      #  self.agent_host.sendCommand("attack 1")
                      #  self.agent_host.sendCommand("jumpstrafe 1")
                      #  self.agent_host.sendCommand("turn 1")
                      #  self.agent_host.sendCommand("move 1")
                      #  self.agent_host.sendCommand("strafe 1")
                      #  self.agent_host.sendCommand("strafe 1")
                      #  kor=kor+1
                      #  print("kor:",kor)
                    #else:
                        print("Westet nezem fordulok jobbra")
                        self.agent_host.sendCommand("turn 1")
                        time.sleep(.2)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.2)
                        fordwest=True
                        kor=kor+1
                        print("kor:",kor)
                elif self.yaw==180 and nbr3x3x3[10]=='dirt' and fordnorth==False:
                   # if nbr3x3x3[12]=='red_flower':
                      #  print("Sarokban toleb balra virag")
                       # self.agent_host.sendCommand("strafe -1")
                       # self.agent_host.sendCommand("attack 1")
                       # self.agent_host.sendCommand("jumpstrafe 1")
                       # self.agent_host.sendCommand("turn 1")
                       # self.agent_host.sendCommand("move 1")
                       # self.agent_host.sendCommand("strafe 1")
                       # self.agent_host.sendCommand("strafe 1")
                       # kor=kor+1
                       # print("kor:",kor)
                    #else:
                        print("Northot nezem fordulok jobbra")
                        self.agent_host.sendCommand("turn 1")
                        time.sleep(.2)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.2)
                        fordnorth=True
                        kor=kor+1
                        print("kor:",kor)
                elif self.yaw==270 and nbr3x3x3[14]=='dirt' and fordeast==False:
                   # if nbr3x3x3[10]=='red_flower':
                    #    print("Sarokban toleb balra virag")
                    #    self.agent_host.sendCommand("strafe -1")
                    #    self.agent_host.sendCommand("attack 1")
                    #    self.agent_host.sendCommand("jumpstrafe 1")
                    #    self.agent_host.sendCommand("turn 1")
                     #   self.agent_host.sendCommand("move 1")
                     #   self.agent_host.sendCommand("strafe 1")
                     #   self.agent_host.sendCommand("strafe 1")
                      #  kor=kor+1
                      #  print("kor:",kor)
                  #  else:
                        print("Eastet nezem fordulok jobbra")
                        self.agent_host.sendCommand("turn 1")
                        time.sleep(.2)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.2)
                        fordeast=True
                        kor=kor+1
                        print("kor:",kor)

                
                #YAW 0
                if self.yaw==0 and (nbr3x3x3[14] == 'red_flower' or nbr3x3x3[17]== 'red_flower'):#tole balra
                    fentkiszedve=True
                    virag=virag+1
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    if virag!=22:
                        self.agent_host.sendCommand("jumpmove 1")
                        time.sleep(.1)
                        print("ugrok")
                        if self.isInTrap(nbr3x3x3) == False:
                            self.agent_host.sendCommand("attack 1")
                            time.sleep(.5)

                    print ("fentkiszedve:",fentkiszedve)
                    print ("virag:",virag)
                    if virag==22:
                        self.agent_host.sendCommand("jumpmove -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)

                    else:
                        self.agent_host.sendCommand("jumpstrafe 1")
                        time.sleep(.2)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)

                    if lentkiszedve == True:
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)
                elif nbr3x3x3[3] == 'red_flower' or nbr3x3x3[6]=='red_flower':#tole jobbra
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("move 1")
                    time.sleep(.2)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print("Godor!")
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    lentkiszedve=True
                    print("lentikiszedve:",lentkiszedve)
                    virag=virag+1
                    print ("virag:",virag)
                    if virag==21:
                        self.agent_host.sendCommand("jumpmove -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("jumpmove -1")
                        time.sleep(.1)
                    #else:
                        #self.agent_host.sendCommand("jumpmove 1")
                        #time.sleep(.1)
                    if fentkiszedve==False:
                        self.agent_host.sendCommand("jumpstrafe -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move 1")
                        time.sleep(.1)
                    else:
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(0.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)

                #YAW 90
                if self.yaw==90 and (nbr3x3x3[16] == 'red_flower' or nbr3x3x3[15]=='red_flower'):#tole balra
                    fentkiszedve=True
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.1)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print("Godor!")
                    print ("fentkiszedve:",fentkiszedve)
                    virag=virag+1
                    print ("virag:",virag)
                    
                    self.agent_host.sendCommand("jumpstrafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    if lentkiszedve == True:
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)
                elif nbr3x3x3[1] == 'red_flower' or nbr3x3x3[0]=='red_flower':#tole jobbra
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("move 1")
                    time.sleep(.2)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print("Godor!")
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    lentkiszedve=True
                    virag=virag+1
                    print ("virag:",virag)
                    #self.agent_host.sendCommand("jumpmove 1")
                    #time.sleep(.1)
                    if fentkiszedve==False:
                        self.agent_host.sendCommand("jumpstrafe -1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move 1")
                        time.sleep(.1)
                    else:
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(0.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)

                #YAW 180
                if self.yaw==180 and (nbr3x3x3[12] == 'red_flower' or nbr3x3x3[9] =='red_flower'):#tole balra
                    fentkiszedve=True
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.1)
                    virag=virag+1
                    print("ugrok")
                    print ("!virag:",virag)
                    if missionXML_file=='nb4tf4i_d.xml':
                        if virag!=25:
                            self.agent_host.sendCommand("attack 1")
                            time.sleep(.5)


                    print ("fentkiszedve:",fentkiszedve)
                    self.agent_host.sendCommand("jumpstrafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    if lentkiszedve == True:
                            if missionXML_file=='nb4tf4i_d.xml':
                                if virag==25:
                                    self.agent_host.sendCommand("jumpmove -1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("turn 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("move 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("move 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("move 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("move 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("strafe 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("strafe 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("strafe 1")
                                    time.sleep(.1)
                                    self.agent_host.sendCommand("strafe 1")
                                    time.sleep(.1)
                                    fordnorth=True
                                    kor=kor+1

                            if virag != 25 or missionXML_file!='nb4tf4i_d.xml':
                                self.agent_host.sendCommand("jumpmove -1")
                                time.sleep(.1)
                                self.agent_host.sendCommand("move -1")
                                time.sleep(.1)
                                self.agent_host.sendCommand("strafe 1")
                                time.sleep(.1)
                                self.agent_host.sendCommand("strafe 1")
                                time.sleep(.1)
                                self.agent_host.sendCommand("strafe 1")
                                time.sleep(.1)
                                self.agent_host.sendCommand("strafe 1")
                                time.sleep(.1)

                            lentkiszedve=False
                            print ("lentkiszedve:",lentkiszedve)
                            fentkiszedve=False
                            print ("fentkiszedve:",fentkiszedve)

                elif nbr3x3x3[5] == 'red_flower' or nbr3x3x3[2]=='red_flower':#tole jobbra
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.4)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print("Godor!")
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    lentkiszedve=True
                    virag=virag+1
                    print ("virag:",virag)
                    #self.agent_host.sendCommand("jumpmove 1")
                    #time.sleep(.1)
                    if fentkiszedve==False:
                        if virag==30:
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("strafe 1")
                            time.sleep(.1)
                            lentkiszedve=False
                        else:
                            self.agent_host.sendCommand("jumpstrafe -1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                    else: 
                        self.agent_host.sendCommand("jumpstrafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(0.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)

                #YAW 270
                if self.yaw==270 and (nbr3x3x3[10] == 'red_flower' or nbr3x3x3[11]=='red_flower'):#tole balra
                    fentkiszedve=True
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.1)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print("Godor!")
                    print ("fentkiszedve:",fentkiszedve)
                    virag=virag+1
                    print ("virag:",virag)
                    
                    self.agent_host.sendCommand("jumpstrafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    if lentkiszedve == True:
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)
                elif nbr3x3x3[7] == 'red_flower' or nbr3x3x3[8]=='red_flower':#tole jobbra
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.2)
                    self.agent_host.sendCommand("attack 1")
                    time.sleep(.5)
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.4)
                    print("ugrok")
                    if self.isInTrap(nbr3x3x3) == False:
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(.5)
                    else: 
                        print ("godor")
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("jumpmove -1")
                    time.sleep(.1)
                    lentkiszedve=True
                    virag=virag+1
                    print ("virag:",virag)
                    #self.agent_host.sendCommand("jumpmove 1")
                    #time.sleep(.1)
                    if fentkiszedve==False:
                        if virag==30:
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("strafe 1")
                            time.sleep(.1)
                            lentkiszedve=False
                            fentkiszedve=True
                        else:
                            self.agent_host.sendCommand("jumpstrafe -1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                            self.agent_host.sendCommand("move 1")
                            time.sleep(.1)
                    else: 
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("move -1")
                        time.sleep(0.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        self.agent_host.sendCommand("strafe 1")
                        time.sleep(.1)
                        lentkiszedve=False
                        print ("lentkiszedve:",lentkiszedve)
                        fentkiszedve=False
                        print ("fentkiszedve:",fentkiszedve)
                #if (kor>4) and (virag==0):
                   # print("    Steve's Coords ahol megunta a kort: ", self.x, self.y, self.z) 
                   # print("\n")
                    #self.agent_host.sendCommand("stafe 1");
                   # time.sleep(.015)
                   # sz=sz+4
                   #kor=0

            #if elso==0:
               # self.agent_host.sendCommand("attack 1")
                #self.agent_host.sendCommand("jumpmove 1")
               # elso=1

            self.agent_host.sendCommand("move 1")
            time.sleep(0.05)

            world_state = self.agent_host.getWorldState()

num_repeats = 1
for ii in range(num_repeats):

    my_mission_record = MalmoPython.MissionRecordSpec()

    # Attempt to start a mission:
    max_retries = 6
    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                print("Attempting to start the mission:")
                time.sleep(2)

    # Loop until mission starts:
    print("   Waiting for the mission to start ")
    world_state = agent_host.getWorldState()

    while not world_state.has_mission_begun:
        print("\r"+hg.cursor(), end="")
        time.sleep(0.15)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)

    print("NB4tf4i Red Flower Hell running\n")
    steve = Steve(agent_host)
    steve.run()

print("Mission ended")
# Mission has ended.
