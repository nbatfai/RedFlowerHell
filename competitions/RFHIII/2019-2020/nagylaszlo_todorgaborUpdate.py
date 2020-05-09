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
# 2020.03.02, https://github.com/nbatfai/RedFlowerHell
# 2020.03.07, "_smartSteve": nof_turn (number of turns) is replaced by the dict self.collectedFlowers 
# 2020.03.11, "_bu": bottom up, s4v3: https://youtu.be/VP0kfvRYD1Y

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
missionXML_file='nb4tf4i_d.xml'
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")    
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n")
    print("Version history\n", "Code: ", sys.argv[0], ", series 4 v.3, bottom up, max 18 poppies. Norbert Bátfai, nbatfai@gmail.com\n")
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
        count=0
        count2=0
        count3=[0]
        self.nof_red_flower = 0

    def move(self,count):
        if count%4==0:
            self.agent_host.sendCommand( "strafe 1" )
            self.agent_host.sendCommand( "strafe 1" )
            self.agent_host.sendCommand( "strafe 1" )
            time.sleep(0.1)
        elif count%4==1:
            self.agent_host.sendCommand( "move -1" )
            self.agent_host.sendCommand( "move -1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(0.1)
        elif count%4==2:
            self.agent_host.sendCommand( "strafe -1" )
            self.agent_host.sendCommand( "strafe -1" )
            self.agent_host.sendCommand( "strafe -1" )
            time.sleep(0.1)
        elif count%4==3:
            self.agent_host.sendCommand( "move 1" )
            self.agent_host.sendCommand( "move 1" )
            self.agent_host.sendCommand( "move 1" )
            time.sleep(0.1)
    def corner(self,nbr):
        a=0
        if nbr[12]=="dirt":
            a=a+1
        if nbr[14]=="dirt":
            a=a+1
        if nbr[10]=="dirt":
            a=a+1
        if nbr[16]=="dirt":
            a=a+1
        if a>1:
            return 1
        if a<2:
            return 0

        
    
    def flowercheck(self,nbr,count2,count,count3):
        if nbr[13]=="red_flower":
            self.agent_host.sendCommand( "attack 1" )
            time.sleep(.6)
            if count%4==0:
                self.agent_host.sendCommand( "jumpmove -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
            elif count%4==1:
                self.agent_host.sendCommand( "jumpstrafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
            elif count%4==2:
                self.agent_host.sendCommand( "jumpmove 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
            elif count%4==3:
                self.agent_host.sendCommand( "jumpstrafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "strafe -1" )
                time.sleep(.05)
            count3[0]=count3[0]+1
            return 2
        elif nbr[12]=="red_flower":
            self.agent_host.sendCommand( "strafe -1" )
            time.sleep(.1)
            return 1
        elif nbr[14]=="red_flower":
            self.agent_host.sendCommand( "strafe 1" )
            time.sleep(.1)
            return 1
        elif nbr[10]=="red_flower" or nbr[9]=="red_flower" or nbr[11]=="red_flower" :
            self.agent_host.sendCommand( "move 1" )
            time.sleep(.1)
            return 1
        elif nbr[16]=="red_flower" or nbr[15]=="red_flower" or nbr[17]=="red_flower":
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.1)
            return 1
        else:
            return 0
        
        
        
            
    
    def run(self):
        # Loop until mission ends:
        world_state = self.agent_host.getWorldState()
        time.sleep(1)
        count=0
        count2=0
        count3=[0]
        if world_state.is_mission_running:
            world_state = self.agent_host.getWorldState()
            time.sleep(0.3)
            if world_state.number_of_observations_since_last_state > 0:
                input = world_state.observations[-1].text
                observations = json.loads(input)
                self.y = int(observations["YPos"])
                self.agent_host.sendCommand( "look 1" )
                time.sleep(.05)
                self.agent_host.sendCommand( "look 1" )
                time.sleep(.05)
                if "Yaw" in observations:
                    self.yaw = int(observations["Yaw"])
                if self.yaw!=180:
                    if self.yaw==90:
                        self.agent_host.sendCommand( "turn 1" )
                        time.sleep(.05)
                    elif self.yaw==0:
                        self.agent_host.sendCommand( "turn 1" )
                        time.sleep(.05)
                        self.agent_host.sendCommand( "turn 1" )
                        time.sleep(.05)
                    elif self.yaw==-90:
                        self.agent_host.sendCommand( "turn -1" )
                        time.sleep(.05)
                while self.y<38:
                    self.agent_host.sendCommand( "jumpmove 1" )
                    time.sleep(.001)
                    self.agent_host.sendCommand( "jumpmove 1" )
                    time.sleep(.001)
                    world_state = self.agent_host.getWorldState()
                    time.sleep(0.05)
                    if world_state.number_of_observations_since_last_state > 0:
                        input = world_state.observations[-1].text
                        observations = json.loads(input)
                        nbr = observations.get("nbr3x3", 0)
                        self.y = int(observations["YPos"])
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.01)
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.01)
            
        while world_state.is_mission_running:
            world_state = self.agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                input = world_state.observations[-1].text
                observations = json.loads(input)
                nbr = observations.get("nbr3x3", 0)
                if count3[0]%2==0:
                    if self.flowercheck(nbr,count2,count,count3)==0:
                        if count2%6==3:
                            if self.corner(nbr)==1:
                                count=count+1
                                count2=0
                        self.move(count)
                        count2=count2+1
                elif count3[0]%2==1:
                    if self.flowercheck(nbr,count2,count,count3)==0:
                        if count2%6==3:
                            if self.corner(nbr)==1:
                                count=count-1
                                count2=0
                        self.move(count-2)
                        count2=count2+1
            else:
                time.sleep(0.1)
           


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
    print("   Waiting for the mission to start")
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
    print("Number of flowers: "+ str(steve.nof_red_flower))
    time.sleep(3)

print("Mission ended")
# Mission has ended.