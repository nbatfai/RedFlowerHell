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
        
        int yaw = 0;

int main(int argc, const char **argv)
{

    int virag = 0;
    int y = 0;

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

    std::ifstream xmlf{"nb4tf4i_d.xml"};
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
    

    for (int i = 0; i < 30; i++)
    {
        agent_host.sendCommand("jumpmove 1");
        boost::this_thread::sleep(boost::posix_time::milliseconds(100));
        agent_host.sendCommand("move 1");
        boost::this_thread::sleep(boost::posix_time::milliseconds(100));
    }
    agent_host.sendCommand("turn 1");
    boost::this_thread::sleep(boost::posix_time::milliseconds(200));
    agent_host.sendCommand("look 1");
    agent_host.sendCommand("look 1");

    // main loop:
    do {

        if(world_state.number_of_observations_since_last_state != 0)
        {
            std::stringstream ss;
            ss << world_state.observations.at(0).get()->text;
            boost::property_tree::ptree pt;
            boost::property_tree::read_json(ss, pt);

            vector<std::string> nbr3x3;

            nbr3x3 = GetItems(world_state,ss,pt);
            for(vector< boost::shared_ptr< TimestampedString>>::iterator it = world_state.observations.begin();it !=world_state.observations.end();++it)
            {
            boost::property_tree::ptree pt;
            istringstream iss((*it)->text);
            boost::property_tree::read_json(iss, pt);

            //string x =pt.get<string>("LineOfSight.type");	
            //string LookingAt =pt.get<string>("XPos");
            //y = pt.get<double>("YPos");
            yaw = pt.get<double>("Yaw");
            //cout<<" Steve's Coords: "<<y<<" "<<yaw<<" "<<"RF:"<<virag;
            }

            calcNbrIndex();

            //checking corners

            if (nbr3x3[front_of_me_idx+9] == "dirt" && nbr3x3[left_of_me_idx+9] == "dirt")
            {
                agent_host.sendCommand("turn 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(300));
            }
            else 
                cout << "\nThere is no corner";

            //checking lava
            if (nbr3x3[left_of_me_idx+18] == "flowing_lava" || nbr3x3[front_of_me_idx+9] == "flowing lava"
                || nbr3x3[front_of_me_idx+18] == "flowing_lava")
            {
                agent_host.sendCommand("strafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("strafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
            }

            //checking traps
            if (nbr3x3[front_of_me_idx+9] == "dirt" && nbr3x3[right_of_me_idx+9] == "dirt" 
                && nbr3x3[left_of_me_idx+9] == "dirt")
            {
                cout << "\nIt's a TRAAAAP";
                agent_host.sendCommand("jumpmove 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
            }

            if (nbr3x3[front_of_me_idx+9] == "dirt" && nbr3x3[left_of_me_idx+9] == "air")
            {
                agent_host.sendCommand("turn 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(200));
                agent_host.sendCommand("jumpstrafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("jumpstrafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
            }

            //finding flower
            if (nbr3x3[front_of_me_idx+9] == "red_flower")
            {
                cout << "\nVIRÁGOT SZEDEK!!";
                agent_host.sendCommand("attack 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(230));
                boost::this_thread::sleep(boost::posix_time::milliseconds(200));
                agent_host.sendCommand("jumpstrafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("jumpstrafe 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
            }

            if (nbr3x3[front_of_me_idx+9] == "air" && nbr3x3[front_of_me_idx] == "dirt")
            {
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
            }


            if (nbr3x3[front_of_me_idx+9] == "air" && nbr3x3[front_of_me_idx] == "air")
            {
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
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
        if (yaw >= 180-22.5 and yaw <= 180+22.5)
        {
            front_of_me_idx = 1;
            front_of_me_idxr = 2;
            front_of_me_idxl = 0;
            right_of_me_idx = 5;
            left_of_me_idx = 3; 
        }
        else if (yaw >= 180+22.5 and yaw <= 270-22.5)
        {
            front_of_me_idx = 2; 
            front_of_me_idxr = 5;
            front_of_me_idxl =1;             
            right_of_me_idx = 8;
            left_of_me_idx = 0;
        }            
        else if (yaw >= 270-22.5 and yaw <= 270+22.5) 
        {
            front_of_me_idx = 5;
            front_of_me_idxr = 8;
            front_of_me_idxl = 2;
            right_of_me_idx = 7;
            left_of_me_idx = 1;   
        }
        else if (yaw >= 270+22.5 and yaw <= 360-22.5)
        {
            front_of_me_idx = 8;            
            front_of_me_idxr = 7;
            front_of_me_idxl = 5;          
            right_of_me_idx = 6;
            left_of_me_idx = 2;    
        }
        else if (yaw >= 360-22.5 or yaw <= 0+22.5)
        {
            front_of_me_idx = 7;
            front_of_me_idxr = 6;
            front_of_me_idxl = 8;
            right_of_me_idx = 3;
            left_of_me_idx = 5;     
        }
        else if (yaw >= 0+22.5 and yaw <= 90-22.5) 
        {
            front_of_me_idx = 6;
            front_of_me_idxr = 3;
            front_of_me_idxl = 7;         
            right_of_me_idx = 0;
            left_of_me_idx = 8;   
        }
        else if (yaw >= 90-22.5 and yaw <= 90+22.5) 
        {
            front_of_me_idx = 3;
            front_of_me_idxr = 0;
            front_of_me_idxl = 6;
            right_of_me_idx = 1;
            left_of_me_idx = 7;    
        }
        else if (yaw >= 90+22.5 and yaw <= 180-22.5)
        {
            front_of_me_idx = 0;
            front_of_me_idxr = 1;
            front_of_me_idxl = 3;
            right_of_me_idx = 2;
            left_of_me_idx = 6;  
        }
        else
            cout<<"There is great disturbance in the Force...";
    }
