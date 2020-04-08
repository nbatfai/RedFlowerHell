from __future__ import print_function
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
    #print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    #print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    #print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    #print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")    
    #print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")    
    #print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    #my_mission.drawBlock( 0, 0, 0, "lava")


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
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0        
        self.yaw = 0
        self.pitch = 0
                    
    def run(self):
        FirstDelay=0.01
        Delay=0.1
        LastDelay=0.5
        NextBlock=""
        Jobb1=""
        Jobb2=""
        Jobb3=""
        Bal_1=""
        Bal_2=""
        Bal_3=""
        virag = 0
        CurrentBlock=""
        erre="turn 1"
        arra="turn -1"
        lastX=0.123
        lastY=0.123
        lastZ=0.123
        lastYAW=123
        
        szint=45
        self.agent_host.sendCommand( "look 1")
        time.sleep(Delay)
        for i in range (8):
            self.agent_host.sendCommand( "move 1" )
            time.sleep(FirstDelay)
        for i in range (szint):
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(FirstDelay)
            self.agent_host.sendCommand( "move 1" )
            time.sleep(FirstDelay)
        self.agent_host.sendCommand( arra )
        time.sleep(FirstDelay)
        for i in range (3+2*szint):
            self.agent_host.sendCommand( "move 1" )
            time.sleep(FirstDelay)
        for k in range (4):
            time.sleep(FirstDelay*10)
            for i in range (6+4*szint):
                for j in range (1):
                    self.agent_host.sendCommand( "move -1" )
                    time.sleep(FirstDelay)
                self.agent_host.sendCommand( "attack 1")
                time.sleep(FirstDelay*2)
            self.agent_host.sendCommand( erre )
        time.sleep(FirstDelay)    
        self.agent_host.sendCommand( arra )
        time.sleep(FirstDelay)  
        for k in range (3):
            self.agent_host.sendCommand( "strafe -1")
            time.sleep(FirstDelay)  
        for k in range (4):
            self.agent_host.sendCommand( "move 1")
            time.sleep(FirstDelay)  
        time.sleep(LastDelay) 
        
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:
        while world_state.is_mission_running:
            #time.sleep(0.001)
            world_state = self.agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                sensations = world_state.observations[-1].text              
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)

                if "Yaw" in observations:
                    self.yaw = int(observations["Yaw"])
                if "Pitch" in observations:
                    self.pitch = int(observations["Pitch"])
                if "XPos" in observations:
                    self.x = observations["XPos"]
                if "ZPos" in observations:
                    self.z = observations["ZPos"]        
                if "YPos" in observations:
                    self.y = observations["YPos"]
                if self.yaw==0:
                    NextBlock=nbr3x3x3[16]
                    Jobb1=nbr3x3x3[15]
                    Jobb2=nbr3x3x3[12]
                    Jobb3=nbr3x3x3[9]
                    Bal_1=nbr3x3x3[8]
                    Bal_2=nbr3x3x3[5]
                    Bal_3=nbr3x3x3[2]
                elif self.yaw==90:
                    NextBlock=nbr3x3x3[12]
                    Jobb1=nbr3x3x3[9]
                    Jobb2=nbr3x3x3[10]
                    Jobb3=nbr3x3x3[11]
                    Bal_1=nbr3x3x3[6]
                    Bal_2=nbr3x3x3[7]
                    Bal_3=nbr3x3x3[8]
                elif self.yaw==180:
                    NextBlock=nbr3x3x3[10]
                    Jobb1=nbr3x3x3[11]
                    Jobb2=nbr3x3x3[14]
                    Jobb3=nbr3x3x3[17]
                    Bal_1=nbr3x3x3[0]
                    Bal_2=nbr3x3x3[3]
                    Bal_3=nbr3x3x3[6]
                elif self.yaw==270:
                    NextBlock=nbr3x3x3[14]
                    Jobb1=nbr3x3x3[17]
                    Jobb2=nbr3x3x3[16]
                    Jobb3=nbr3x3x3[15]
                    Bal_1=nbr3x3x3[2]
                    Bal_2=nbr3x3x3[1]
                    Bal_3=nbr3x3x3[0]
                else:
                    print("Yaw Error!")
                #CurrentBlock=nbr3x3x3[13]
                
                if (lastX!=self.x or lastY!=self.y or lastZ!=self.z or lastYAW!=self.yaw) and self.pitch==45:
                    self.agent_host.sendCommand( "look 1")
                    time.sleep(FirstDelay)
                    fordult=False
                    #print(lastX-self.x, lastY-self.y, lastZ-self.z, self.pitch)
                    lastX=self.x
                    lastY=self.y
                    lastZ=self.z
                    lastYAW=self.yaw
                    #print("    Steve's Coords: ", self.x, self.y, self.z, self.yaw, NextBlock)        
                    #if Jobb1== "red_flower" or Jobb2== "red_flower" or Jobb3== "red_flower" or  Bal_1== "red_flower" or Bal_2== "red_flower" or Bal_3== "red_flower":

                    if Bal_1== "red_flower":
                        self.agent_host.sendCommand( "strafe -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand( "move 1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay)
                        self.agent_host.sendCommand( "jumpmove -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand( "jumpstrafe 1")
                        virag = virag+1
                        
                    if Bal_2== "red_flower":
                        self.agent_host.sendCommand( "strafe -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay)
                        if Bal_1=="dirt":
                            self.agent_host.sendCommand( "jumpmove -1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "jumpstrafe 1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "move 1")
                        else:
                            self.agent_host.sendCommand( "jumpmove 1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "jumpstrafe 1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "move -1")
                        virag = virag+1
                        
                    if Bal_3== "red_flower":
                        self.agent_host.sendCommand( "strafe -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand( "move -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay) 
                        if Bal_2=="dirt":
                            self.agent_host.sendCommand( "jumpmove -1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "jumpstrafe 1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "move 1")
                            time.sleep(FistDelay)
                            self.agent_host.sendCommand( "move 1")
                        else:
                            self.agent_host.sendCommand( "jumpmove 1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "jumpstrafe 1")
                        virag = virag+1
                        
                    if Jobb1== "red_flower":
                        self.agent_host.sendCommand( "strafe 1")
                        time.sleep(FirstDelay)
                        self.agent_host.sendCommand( "move 1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay)
                        self.agent_host.sendCommand( "jumpstrafe -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand( "move -1")
                        virag = virag+1
                            
                    if Jobb2== "red_flower":
                        self.agent_host.sendCommand( "strafe 1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay)
                        self.agent_host.sendCommand( "jumpstrafe -1")
                        time.sleep(Delay)
                        virag = virag+1
                            
                    if Jobb3== "red_flower":
                        self.agent_host.sendCommand( "strafe 1")
                        time.sleep(FirstDelay)
                        self.agent_host.sendCommand( "move -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand("attack 1")
                        time.sleep(LastDelay)
                        self.agent_host.sendCommand( "jumpstrafe -1")
                        time.sleep(Delay)
                        self.agent_host.sendCommand( "move 1")
                        virag = virag+1
                        
                            
                    if Jobb1== "red_flower" or Jobb2== "red_flower" or Jobb3== "red_flower":
                        if virag==1:
                            if Bal_2== "dirt":
                                    self.agent_host.sendCommand( "move -1")
                                    time.sleep(Delay)
                            self.agent_host.sendCommand( "strafe -1")
                            time.sleep(Delay)
                            self.agent_host.sendCommand( "strafe -1")
                            time.sleep(Delay)
                            virag=0
                        elif virag==2:
                            for i in range(5):
                                self.agent_host.sendCommand( "move -1")
                                time.sleep(FirstDelay)
                            for i in range(4):
                                self.agent_host.sendCommand( "strafe -1")
                                time.sleep(FirstDelay)
                            virag=0
                            
                    if NextBlock=="dirt" and self.y==3:
                        self.agent_host.sendCommand("move -1")
                        time.sleep(FirstDelay)
                        self.agent_host.sendCommand("strafe -1")
                        time.sleep(FirstDelay)
                        self.agent_host.sendCommand(arra)
                        time.sleep(FirstDelay)
                    if Bal_2== "dirt" and Bal_1== "dirt" and self.y!=3:
                        if Bal_3=="dirt":
                            self.agent_host.sendCommand("move -1")
                            time.sleep(FirstDelay)
                        self.agent_host.sendCommand( arra )
                        time.sleep(Delay)
                        fordult=True
                    
                    if fordult==False:  
                        for i in range(3):
                            self.agent_host.sendCommand("move 1")
                            time.sleep(FirstDelay)
                    time.sleep(FirstDelay)
                    self.agent_host.sendCommand( "look -1")
                    


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
