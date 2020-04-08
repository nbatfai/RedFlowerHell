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

#-------------------------------------------------------------------------------------------------------------------------------#
class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.y=0
        self.yaw = 0  

        self.elottem=0
        self.elottembalra=0
        self.elottemjobbra=0
        self.mogottem=0
        self.mogottembalra=0
        self.mogottemjobbra=0
        self.jobbra=0
        self.balra=0

        self.virag=0
        self.seged=1

        self.n=41
        self.max=0

        self.szint={}
        self.szint[1]=True
        self.szint[2]=True

    def nbrindex(self):
        if self.yaw ==180:
            self.elottembalra = 0
            self.elottem = 1
            self.elottemjobbra = 2
            self.balra= 3
            self.jobbra = 5
            self.mogottembalra=6 
            self.mogottem=7
            self.mogottemjobbra=8       
        elif self.yaw ==270: 
            self.elottembalra = 2
            self.elottem = 5
            self.elottemjobbra = 8
            self.balra= 1
            self.jobbra = 7
            self.mogottembalra=0
            self.mogottem=3
            self.mogottemjobbra=6
        elif self.yaw ==0: 
            self.elottembalra = 8
            self.elottem = 7
            self.elottemjobbra = 6
            self.balra= 5
            self.jobbra = 3
            self.mogottembalra=2
            self.mogottem=1
            self.mogottemjobbra=0   
        else:
            self.elottembalra = 6
            self.elottem = 3
            self.elottemjobbra = 0
            self.balra= 7
            self.jobbra = 1
            self.mogottembalra=8
            self.mogottem=5
            self.mogottemjobbra=2  

    def felmegy(self):
        for i in range(self.n):
            self.agent_host.sendCommand( "move 1" )
            time.sleep(0.01)   
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(0.01)   
        self.agent_host.sendCommand( "turn -1" )
        time.sleep(0.2)   

    def falelottem(self,nbr):
        if nbr[self.elottembalra+9]=="dirt" and nbr[self.elottem+9]=="dirt" and nbr[self.elottemjobbra+9]=="dirt":
            return True
        else: 
            return False

    def trap(self,nbr):
        db=0
        for i in range(9):
            if nbr[i+9]=="dirt":
                db+=1
        if db>5:
            return True
        else:
            return False

    def felvesz(self):
        self.agent_host.sendCommand("attack 1")
        time.sleep(0.3)

    def inventory(self, observations):
        self.virag=observations.get('Hotbar_1_size', "")
        if self.virag==self.seged:
            self.szint[self.y]=True
            self.seged+=1
            return True
        else:
            return False

    def szintvalt(self,nbr):
        if self.szint[self.y+1]:
            if self.szint[self.y-1]:
                for i in range(4):
                    self.agent_host.sendCommand( "strafe -1" )   
                    time.sleep(0.1)
            else:
                for i in range(2):
                    self.agent_host.sendCommand( "strafe -1" )   
                    time.sleep(0.1)
        elif not self.szint[self.y+1]:
            self.agent_host.sendCommand( "strafe 1" )   
            time.sleep(0.1)
            self.agent_host.sendCommand( "jumpstrafe 1" )   
            time.sleep(0.1)

    def lava(self,nbr):
        if nbr[self.elottemjobbra+9]=="flowing_lava" or nbr[self.elottem+9]=="flowing_lava":
            return True
        else:
            return False
 
    def run(self):
        world_state = self.agent_host.getWorldState()

        self.agent_host.sendCommand( "turn -1" )   
        time.sleep(0.1) 
        #self.agent_host.sendCommand( "turn -1" )   
        #time.sleep(0.1) 

        self.agent_host.sendCommand( "look 1" )   
        time.sleep(0.1) 
        self.agent_host.sendCommand( "look 1" )   
        time.sleep(0.1) 

        self.agent_host.sendCommand( "attack 1" )   
        time.sleep(0.1)

        self.agent_host.sendCommand( "jumpstrafe 1" )   
        time.sleep(0.01)

        self.felmegy()

        while world_state.is_mission_running:
            self.main(world_state)
            world_state = self.agent_host.getWorldState()

    def main(self,world_state):
        if world_state.number_of_observations_since_last_state == 0:
            return

        observations = json.loads(world_state.observations[-1].text) 
        nbr = observations.get("nbr3x3", 0)
        if "Yaw" in observations:
            self.yaw = int(observations["Yaw"])     
        if "YPos" in observations:
            self.y = int(observations["YPos"])

        self.nbrindex()

        if self.max==0:
            self.max=self.y
            for i in range(self.max+1):
                self.szint[i]=False
            for i in range(self.max+1,70,1):
                self.szint[i]=True
    
        if self.trap(nbr):
            self.agent_host.sendCommand( "jumpuse 1" )   
            time.sleep(0.1) 
            self.agent_host.sendCommand( "strafe -1" )   
            time.sleep(0.1)
            return
        
        if self.inventory(observations):
            self.szintvalt(nbr)
            return
        
        if self.szint[self.y] and self.szint[self.y+1]:
            self.agent_host.sendCommand( "turn -1" )
            time.sleep(0.1)   
            self.szintvalt(nbr)
            time.sleep(0.2)
            return

        if "red_flower" in nbr:
            if nbr[self.elottembalra]=="red_flower" or nbr[self.elottembalra+9]=="red_flower":
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                self.felvesz() 
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.elottemjobbra+9]=="red_flower":
                self.agent_host.sendCommand( "strafe 1" )   
                time.sleep(0.1)
                self.felvesz() 
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.elottem+9]=="red_flower":
                self.felvesz()
                return
            if nbr[self.balra]=="red_flower" or nbr[self.balra]=="red_flower":
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                self.agent_host.sendCommand("move -1")
                time.sleep(0.1)
                self.felvesz()
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.jobbra+9]=="red_flower":
                self.agent_host.sendCommand( "strafe 1" )   
                time.sleep(0.1)  
                self.agent_host.sendCommand("move -1")
                time.sleep(0.1)
                self.felvesz()
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.mogottemjobbra+9]=="red_flower":
                self.agent_host.sendCommand("strafe 1")
                time.sleep(0.1)
                self.agent_host.sendCommand("move -1")
                time.sleep(0.1)
                #self.agent_host.sendCommand("move -1")
                #time.sleep(0.1)
                self.felvesz()
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.mogottembalra]=="red_flower" or nbr[self.mogottembalra+9]=="red_flower":
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.1)
                self.agent_host.sendCommand("move -1")
                time.sleep(0.1)
                #self.agent_host.sendCommand("move -1")
                #time.sleep(0.1)
                self.felvesz()
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[self.mogottem+9]=="red_flower":
                self.agent_host.sendCommand("move -1")
                time.sleep(0.1)
                #self.agent_host.sendCommand("move -1")
                #time.sleep(0.1)
                self.felvesz()
                self.agent_host.sendCommand( "strafe -1" )   
                time.sleep(0.1)
                return
            if nbr[13]=="red_flower":
                self.felvesz()
            return

        if self.lava(nbr):
            self.agent_host.sendCommand( "strafe -1" )   
            time.sleep(0.1) 
            self.agent_host.sendCommand( "strafe -1" )   
            time.sleep(0.1) 
            return

        if self.falelottem(nbr):
            self.agent_host.sendCommand( "turn -1" )
            time.sleep(0.1) 
            self.agent_host.sendCommand( "strafe -1" )   
            time.sleep(0.1) 
            return

        self.agent_host.sendCommand( "move 1" )
        time.sleep(0.015)   

#-------------------------------------------------------------------------------------------------------------------------------#
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
