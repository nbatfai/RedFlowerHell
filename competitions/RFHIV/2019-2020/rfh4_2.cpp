// --------------------------------------------------------------------------------------------------
//  Copyright (c) 2016 Microsoft Corporation
//  
//  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
//  associated documentation files (the "Software"), to deal in the Software without restriction,
//  including without limitation the rights to use, copy, modify, merge, publish, distribute,
//  sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//  
//  The above copyright notice and this permission notice shall be included in all copies or
//  substantial portions of the Software.
//  
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
//  NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
//  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
//  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// --------------------------------------------------------------------------------------------------

// Malmo:
#include <AgentHost.h>
#include <ClientPool.h>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/foreach.hpp>
using namespace malmo;

// STL:
#include <cstdlib>
#include <exception>
#include <iostream>
using namespace std;

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>


vector<string> GetItems(WorldState world_state,std::stringstream & ss, boost::property_tree::ptree & pt)
{
    vector<string> nbr3x3;

    ss.clear();
    pt.clear();

    ss << world_state.observations.at(0).get()->text;
    boost::property_tree::read_json(ss, pt);
    BOOST_FOREACH(boost::property_tree::ptree::value_type &v, pt.get_child("nbr3x3"))
    {
        assert(v.first.empty());
        nbr3x3.push_back(v.second.data());
    }

    return nbr3x3;
}
    void calcNbrIndex();
        int front_of_me_idx = 0;
        int front_of_me_idxr = 0;
        int front_of_me_idxl = 0;        
        int right_of_me_idx = 0;
        int left_of_me_idx = 0; 
        int behind_of_me_idx = 0;
        
        int yaw = 0;

int main(int argc, const char **argv)
{
	int y = 0;

	int kills = 0;

	int delay = 0;

    //string lookingAt;

	/*enum class SteveState
	{
		PREPARE = 0,
		TURN = 1,
		FIXTURN = 2,
		FORWARD = 3,
		FLOWER = 4,
		PICKUP = 5,
		STUCK = 6,
		LVL_UP = 7,
		KILLING_ZOMBIES = 8,
		MASTER_ROTATION = 9,
		MOVE_TO_DIR = 10,

		STOP = 20
	}*/

    //SteveState => st
	string st = "PREPARE";

    AgentHost agent_host;

    try
    {
        agent_host.parseArgs(argc, argv);
    }
    catch( const exception& e )
    {
        cout << "ERROR: " << e.what() << endl;
        cout << agent_host.getUsage() << endl;
        return EXIT_SUCCESS;
    }
    if( agent_host.receivedArgument("help") )
    {
        cout << agent_host.getUsage() << endl;
        return EXIT_SUCCESS;
    }

    std::ifstream xmlf{"nb4tf4i_d4_Rudolf_hard.xml"};
    std::string xml{std::istreambuf_iterator<char>(xmlf), std::istreambuf_iterator<char>()};

    MissionSpec my_mission{xml, true};
    

    MissionRecordSpec my_mission_record("./saved_data.tgz");
    

    int attempts = 0;
    bool connected = false;
    do {
        try {
            agent_host.startMission(my_mission, my_mission_record);
            connected = true;
        }
        catch (exception& e) {
            cout << "Error starting mission: " << e.what() << endl;
            attempts += 1;
            if (attempts >= 3)
                return EXIT_FAILURE;    // Give up after three attempts.
            else
                boost::this_thread::sleep(boost::posix_time::milliseconds(1000));   // Wait a second and try again.
        }
    } while (!connected);

    WorldState world_state;

    cout << "Waiting for the mission to start" << flush;
    do {
        cout << "." << flush;
        boost::this_thread::sleep(boost::posix_time::milliseconds(100));
        world_state = agent_host.getWorldState();
        for( boost::shared_ptr<TimestampedString> error : world_state.errors )
            cout << "Error: " << error->text << endl;
    } while (!world_state.has_mission_begun);
    cout << endl;
    
    // main loop:
    do {

        if(world_state.number_of_observations_since_last_state != 0)
        {

			boost::this_thread::sleep(boost::posix_time::milliseconds(delay));

            std::stringstream ss;
            ss << world_state.observations.at(0).get()->text;
            boost::property_tree::ptree pt;
            boost::property_tree::read_json(ss, pt);

            vector<std::string> nbr3x3;

            nbr3x3 = GetItems(world_state,ss,pt);
            for (vector<boost::shared_ptr<TimestampedString>>::iterator it = world_state.observations.begin();
                it != world_state.observations.end(); ++it)
            {
                boost::property_tree::ptree pt;
                istringstream iss((*it)->text);
                boost::property_tree::read_json(iss, pt);

                kills = pt.get<int>("MobsKilled");
                y = pt.get<double>("YPos");
                yaw = pt.get<double>("Yaw");
            }

            calcNbrIndex();
        
            if (st == "PREPARE")
			{
				agent_host.sendCommand("move -1");
				agent_host.sendCommand("turn -1");
				boost::this_thread::sleep(boost::posix_time::milliseconds(250));
				agent_host.sendCommand("turn 0");
				boost::this_thread::sleep(boost::posix_time::milliseconds(2500));
				agent_host.sendCommand("move 0");
				agent_host.sendCommand("hotbar.3 1");
				st = "KILLING_ZOMBIES";
			}

			else if (st == "KILLING_ZOMBIES")
			{
                for (vector<boost::shared_ptr<TimestampedString>>::iterator it = world_state.observations.begin();
                    it != world_state.observations.end(); ++it)
                {
                    boost::property_tree::ptree pt;
                    istringstream iss((*it)->text);
                    boost::property_tree::read_json(iss, pt);

                    string lookingAt = pt.get<string>("LineOfSight.type");	
                    string x = pt.get<string>("XPos");

                    if (lookingAt == "Zombie")
                    {
                        agent_host.sendCommand("turn 0");
                        cout << "OH, EGY ZOMBI.. " << endl;
                        agent_host.sendCommand("attack 1");
                        boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                        agent_host.sendCommand("attack 0");
                        delay = 10;
                    }
                    if (kills >= 2)
                    {
                        agent_host.sendCommand("turn 0");
                        st = "MASTER_ROTATION";
                    }
                }
			}

			else if (st == "MASTER_ROTATION")
			{
				if (yaw > 85 && yaw <= 95)
				{
					cout << "Yaw: " << yaw << endl;
					boost::this_thread::sleep(boost::posix_time::milliseconds(20));
					agent_host.sendCommand("turn 0");
					boost::this_thread::sleep(boost::posix_time::milliseconds(500));
					agent_host.sendCommand("strafe -1");
					if (nbr3x3[left_of_me_idx+9] == "bedrock")
					{
						agent_host.sendCommand("strafe 1");
						boost::this_thread::sleep(boost::posix_time::milliseconds(500));
						agent_host.sendCommand("strafe 0");
						st = "LVL_UP";
					}
				}
				else 
				{
					agent_host.sendCommand("turn 0.1");
					delay = 10;
				}
			}

            else if (st == "LVL_UP")
            {
                if (nbr3x3[front_of_me_idx+18] != "bedrock")
                {
                    agent_host.sendCommand("move 1");
                    agent_host.sendCommand("jump 1");
                }
                else 
                {
                    agent_host.sendCommand("jump 0");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(3000));
                    agent_host.sendCommand("move 0");
                    agent_host.sendCommand("strafe 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(250));
                    agent_host.sendCommand("strafe 0");
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                    agent_host.sendCommand("turn 0");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                    if (y <= 12)
                    {
                        agent_host.sendCommand("move 1");
                        agent_host.sendCommand("jump 1");
                    }
                    else
                    {
                        agent_host.sendCommand("jump 0");
                        agent_host.sendCommand("move 0");
                        boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
                        st = "TURN";
                    }
                }
            }

            else if (st == "TURN")
            {
                agent_host.sendCommand("turn 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                agent_host.sendCommand("turn 0");
                boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                st = "FIXTURN";
            }

            else if (st == "FIXTURN")
            {
                if (yaw >= 45 && yaw <= 135)
                {
                    if (yaw < 80)
                    {
                        agent_host.sendCommand("turn 0.2");
                        delay = 10;
                    }
                    else 
                    {
                        agent_host.sendCommand("turn 0");
                        st = "FORWARD";
                    }
                }
                else if (yaw >= 135 && yaw <= 225)
                {
                    if (yaw < 170)
                    {
                        agent_host.sendCommand("turn 0.2");
                        delay = 10;
                    }
                    else 
                    {
                        agent_host.sendCommand("turn 0");
                        st = "FORWARD";
                    }
                }
                else if (yaw >= 225 && yaw <= 315)
                {
                    if (yaw < 260)
                    {
                        agent_host.sendCommand("turn 0.2");
                        delay = 10;
                    }
                    else 
                    {
                        agent_host.sendCommand("turn 0");
                        st = "FORWARD";
                    }
                }
                else 
                {
                    if (yaw > 350 || yaw < 10)
                    {
                        agent_host.sendCommand("turn 0");
                        st = "FORWARD";
                    }
                    else 
                    {
                        agent_host.sendCommand("turn 0.2");
                        delay = 10;
                    }
                }
            }

            else if (st == "FORWARD")
            {
                agent_host.sendCommand("move 0");

                if (nbr3x3[4] == "grass")
                {
                    agent_host.sendCommand("move -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(180));
                    agent_host.sendCommand("move 0");
                    cout << "VIRAAAG" << endl;
                    st = "FLOWER";
                }

                else if (nbr3x3[front_of_me_idx+9] == "bedrock")
                {
                    if (nbr3x3[right_of_me_idx+9] == "bedrock")
                    {
                        st = "STUCK";
                    }
                    else 
                    {
                        agent_host.sendCommand("move 0");
                        st = "TURN";
                        boost::this_thread::sleep(boost::posix_time::milliseconds(500));
                    }
                }

                else 
                {
                    agent_host.sendCommand("move 1");
                }

                delay = 10;
            }

            else if (st == "FLOWER")
            {
                if (nbr3x3[4] != "grass")
                {
                    st = "PICKUP";
                }
                else 
                {
                    agent_host.sendCommand("move 0");
                    agent_host.sendCommand("pitch 1");
                    agent_host.sendCommand("attack 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(1300));
                    st = "PICKUP";
                }
            }

            else if (st == "PICKUP")
            {
                if (nbr3x3[front_of_me_idx+9] == "bedrock" && nbr3x3[behind_of_me_idx+9] == "bedrock")
                {
                    agent_host.sendCommand("attack 0");
                    st = "STUCK";
                }
                else
                {
                    agent_host.sendCommand("strafe -1");
                    agent_host.sendCommand("move -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(700));
                    agent_host.sendCommand("strafe 0");
                    agent_host.sendCommand("move 0");
                    st = "FLOWER";
                }
            }

            else if (st == "STUCK")
            {
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(400));
                agent_host.sendCommand("jump 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(300));
                agent_host.sendCommand("jump 0");
                agent_host.sendCommand("move 0");
                st = "FORWARD";
            }
        }

        world_state = agent_host.getWorldState();
        for( boost::shared_ptr<TimestampedString> error : world_state.errors )
            cout << "Error: " << error->text << endl;

        
    } while (world_state.is_mission_running);

    cout << "Mission has stopped." << endl;

    return EXIT_SUCCESS;

}

void calcNbrIndex()
    {
        if (yaw >= 180 - 30 and yaw <= 180 + 30)
        {
            front_of_me_idx = 1;
            front_of_me_idxr = 2;
            front_of_me_idxl = 0;
            right_of_me_idx = 5;
            left_of_me_idx = 3;
            behind_of_me_idx = 7;
        }
        else if (yaw >= 270 - 30 and yaw <= 270 + 30) 
        {
            front_of_me_idx = 5;
            front_of_me_idxr = 8;
            front_of_me_idxl = 2;
            right_of_me_idx = 7;
            left_of_me_idx = 1;   
            behind_of_me_idx = 3;
        }
        else if (yaw >= 360 - 30 or yaw <= 0 + 30)
        {
            front_of_me_idx = 7;
            front_of_me_idxr = 6;
            front_of_me_idxl = 8;
            right_of_me_idx = 3;
            left_of_me_idx = 5;
            behind_of_me_idx = 1; 
        }
        else if (yaw >= 90-30 and yaw <= 90+30) 
        {
            front_of_me_idx = 3;
            front_of_me_idxr = 0;
            front_of_me_idxl = 6;
            right_of_me_idx = 1;
            left_of_me_idx = 7;
            behind_of_me_idx = 5;
        }
        else
            cout<<"Something wrong I can feel it.. ";
    }
