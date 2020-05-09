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
# 2020.03.07, "_smartSteve": nof_turn (number of turns) is replaced by the dict self.collectedFlowers 
# 2020.03.29, Red Pill team, Nándor Bátfai & Norbert Bátfai, rewriting from scratch: https://youtu.be/5-0fsgvyZ9c, "smart" feature is eliminated
# 2020.03.31, Green Pill team, Norbert Bátfai, forked from Red Pill, https://youtu.be/BCS1_TuMsRQ
# 2020.04.02, Qualification for participating in RFH III, Norbert Bátfai, https://youtu.be/cfhh3llDoRo
# 2020.04.03, Uploading to github repo https://github.com/nbatfai/RedFlowerHell 


# TODO életerőtől függő viselkedés

from builtins import range
import MalmoPython
import os
import sys
import time
import random
import json
import math
from enum import Enum

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
missionXML_file=sys.argv[1]
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell IV Rudolph \"Hard League\") - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")    
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n")
    print("Version history\n", "Code: Green Pill", sys.argv[0], ", max 4 poppies: https://youtu.be/ZTsXkMh3pqQ, Norbert Bátfai, nbatfai@gmail.com, Nándor Bátfai.\n")
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

class SteveState(Enum): 
    GOING_UP = 0
    FIRST_TURN = 1
    FORWARD = 2
    TURNING = 3
    FLOWER = 4
    ATTACK = 5
    PICK_UP = 6
    LVL_DOWN = 7
    KILLING_ZOMBIES = 8
    GOING_TO_CORNER = 9
    ALIGN = 10
    TURNING2 = 11

class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.life = 0

        self.state = SteveState.GOING_TO_CORNER
        
        self.front_of_me_idx = 0
        self.front_of_me_idxr = 0
        self.front_of_me_idxl = 0        
        self.right_of_me_idx = 0
        self.left_of_me_idx = 0        
        self.behind_of_me_idxr = 0
        self.behind_of_me_idxl = 0        
        
        self.nof_red_flower = 0

        self.mustKill = 2
        self.mobs_killed = 0
        self.flip = 0

    def isInTrap(self, nbr):            
        dc = 0    
        nbri = [9,10,11,12,14,15,16,17]    
        for i in range(0, len(nbri)):
            if nbr[nbri[i]]=="bedrock" :
                dc = dc + 1            
        return dc > 6

    def checkInventory(self, observations):
        flower = False
        dirt = False
        dirt_idx = 0
        for i in range(8):
            hotbari = 'Hotbar_'+str(i)+'_item'
            hotbars = 'Hotbar_'+str(i)+'_size'
            slot0_contents = observations.get(hotbari, "")
            if slot0_contents == "red_flower":
                slot0_size = observations.get(hotbars, "")
                if self.nof_red_flower < slot0_size :
                    self.nof_red_flower = slot0_size                                            
                    print("   *** A RED FLOWER IS MINED AND PICKED UP *** ")
                    flower = True
                    
                    if self.pitch != 0:
                        self.agent_host.sendCommand( "pitch -1" );                    
            if slot0_contents == "dirt":
                dirt_idx = i+1
                slot0_size = observations.get(hotbars, "")
                if 0 < slot0_size :
                    dirt = True
                    
        return flower, dirt, dirt_idx        
                
    def idle(self, delay):
        #print("      SLEEPING for ", delay)
        time.sleep(delay)

    def calcNbrIndex(self):
        if self.yaw >= 180-22.5 and self.yaw <= 180+22.5 :
            self.front_of_me_idx = 1
            self.front_of_me_idxr = 2
            self.front_of_me_idxl = 0
            self.right_of_me_idx = 5
            self.left_of_me_idx = 3            
            self.behind_of_me_idxr = 8
            self.behind_of_me_idxl = 6
        elif self.yaw >= 180+22.5 and self.yaw <= 270-22.5 :
            self.front_of_me_idx = 2 
            self.front_of_me_idxr = 5
            self.front_of_me_idxl =1             
            self.right_of_me_idx = 8
            self.left_of_me_idx = 0            
            self.behind_of_me_idxr = 7
            self.behind_of_me_idxl = 3
        elif self.yaw >= 270-22.5 and self.yaw <= 270+22.5 :
            self.front_of_me_idx = 5
            self.front_of_me_idxr = 8
            self.front_of_me_idxl = 2
            self.right_of_me_idx = 7
            self.left_of_me_idx = 1   
            self.behind_of_me_idxr = 6
            self.behind_of_me_idxl = 0            
        elif self.yaw >= 270+22.5 and self.yaw <= 360-22.5 :
            self.front_of_me_idx = 8            
            self.front_of_me_idxr = 7
            self.front_of_me_idxl = 5          
            self.right_of_me_idx = 6
            self.left_of_me_idx = 2   
            self.behind_of_me_idxr = 3
            self.behind_of_me_idxl = 1
            
        elif self.yaw >= 360-22.5 or self.yaw <= 0+22.5 :
            self.front_of_me_idx = 7
            self.front_of_me_idxr = 6
            self.front_of_me_idxl = 8
            self.right_of_me_idx = 3
            self.left_of_me_idx = 5   
            self.behind_of_me_idxr = 0
            self.behind_of_me_idxl = 2
            
        elif self.yaw >= 0+22.5 and self.yaw <= 90-22.5 :
            self.front_of_me_idx = 6
            self.front_of_me_idxr = 3
            self.front_of_me_idxl = 7          
            self.right_of_me_idx = 0
            self.left_of_me_idx = 8   
            self.behind_of_me_idxr = 1
            self.behind_of_me_idxl = 5
            
        elif self.yaw >= 90-22.5 and self.yaw <= 90+22.5 :
            self.front_of_me_idx = 3
            self.front_of_me_idxr = 0
            self.front_of_me_idxl = 6
            self.right_of_me_idx = 1
            self.left_of_me_idx = 7   
            self.behind_of_me_idxr = 2
            self.behind_of_me_idxl = 8
            
        elif self.yaw >= 90+22.5 and self.yaw <= 180-22.5 :
            self.front_of_me_idx = 0
            self.front_of_me_idxr = 1
            self.front_of_me_idxl = 3
            self.right_of_me_idx = 2
            self.left_of_me_idx = 6   
            self.behind_of_me_idxr = 7
            self.behind_of_me_idxl = 5
            
        else:
            print("There is great disturbance in the Force...")            

    def whatISee(self, observations):
        self.lookingat = "NOTHING"            
        if "LineOfSight" in observations:
            lineOfSight = observations["LineOfSight"] 
            self.lookingat = lineOfSight["type"]      

    def whatMyPos(self, observations):
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

    def prepForAttack(self):
        self.agent_host.sendCommand( "move 0" )
        self.pitch90()

    def pitch0(self):
        if self.pitch > -10 and self.pitch < 10:
            self.agent_host.sendCommand( "pitch 0" )
        elif self.pitch <= -10 :
            self.agent_host.sendCommand( "pitch .6" )
        else :
            self.agent_host.sendCommand( "pitch -.6" )

    def pitch90(self):
        if self.pitch < 90:
            self.agent_host.sendCommand( "pitch 1" )

    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:
        while world_state.is_mission_running:
            
            #print(">>> nb4tf4i arena -----------------------------------\n")
            delay = self.action(world_state)
            #print("nb4tf4i arena >>> -----------------------------------\n")
            self.idle(delay)
                                
            world_state = self.agent_host.getWorldState()

    def action(self, world_state):
        for error in world_state.errors:
            print("Error:", error.text)
        
        if world_state.number_of_observations_since_last_state == 0:
            #print("    NO OBSERVATIONS NO ACTIONS")
            return False
        
        input = world_state.observations[-1].text
        observations = json.loads(input)
        nbr = observations.get("nbr3x3", 0)
        #print(observations)
        
        self.whatMyPos(observations)
        print("\n>>> nb4tf4i arena --- (there are observations) -------------------")
        print("Steve's Coords: ", self.x, self.y, self.z, " Yaw: ", self.yaw, " Pitch: ", self.pitch, " #RF: ", self.nof_red_flower)        

        flower, dirt, dirt_idx = self.checkInventory(observations)
        #print("Number of flowers: ", self.nof_red_flower)

        self.whatISee(observations)
        print("    Steve's <): ", self.lookingat)

        if "Life" in observations:
            life = int(observations["Life"])
        if "MobsKilled" in observations:
            self.mobs_killed = int(observations["MobsKilled"])

        print("LIFE: ", life, " #Mobs: ", self.mobs_killed, " #RF: ", self.nof_red_flower)
                        
        self.calcNbrIndex()                
        
        delay = .2
                                
        if self.state == SteveState.GOING_TO_CORNER :

            print(" GOING_TO_CORNER: ")

            if nbr[self.front_of_me_idx+9] != "bedrock" :                
                print("   THERE IS NO OBSTACLE IN FRONT OF ME ")
                self.agent_host.sendCommand( "turn 0" )
                self.agent_host.sendCommand( "move 1" )                                            
            elif nbr[self.left_of_me_idx+9] != "bedrock" :
                print("   THERE IS AN OBSTACLE IN FRONT OF ME ")    
                self.agent_host.sendCommand( "move 0" )                                            
                self.agent_host.sendCommand( "turn .3" )                
                self.state = SteveState.FIRST_TURN
            else :   
                print("   I AM IN THE CORNER ")    
                self.agent_host.sendCommand( "move 0" )                                            
                self.state = SteveState.KILLING_ZOMBIES
  
            delay = .1

            
        elif self.state == SteveState.FIRST_TURN:
                        
            print(" FIRST_TURN: ", nbr[self.front_of_me_idx+9])
            
            if nbr[self.left_of_me_idx+9] != "bedrock":
                print("   TURNING ")
                self.agent_host.sendCommand( "turn .3" )               
            elif nbr[self.front_of_me_idx+9] != "air" :    
                print("   TURNING (redundant)")
                self.agent_host.sendCommand( "turn .3" )               
            else:    
                print("   TURNED ")
                self.agent_host.sendCommand( "turn 0" )               
                self.state = SteveState.GOING_TO_CORNER
                        
            delay = .1

                
        elif self.state == SteveState.KILLING_ZOMBIES :

            self.agent_host.sendCommand( "hotbar.3 1")

            print(" KILLING_ZOMBIES: ") 

            self.agent_host.sendCommand( "hotbar.3 1")
            self.agent_host.sendCommand( "hotbar.3 0")

            if self.lookingat == "Zombie":
                print("   I CAN SEE A ZOMBIE!!!!!!!!!!")
                self.agent_host.sendCommand( "move 0" )                                
                self.agent_host.sendCommand( "turn 0" )
                self.agent_host.sendCommand( "attack 1" )                
                            
            elif nbr[self.behind_of_me_idxr+9] == "bedrock" and nbr[self.behind_of_me_idxl+9] == "bedrock" :
                print("   I AM ATTACKING IN THE CORNER ")

                self.agent_host.sendCommand( "attack 1" )             
                self.flip = (self.flip + 1) % 2
                                
                if self.flip == 0:                
                    self.agent_host.sendCommand( "turn -.3" )
                else: 
                    self.agent_host.sendCommand( "turn .4" )
                
            else:   
                print("   I AM LOOKING FOR ZOMBIES ")
                self.agent_host.sendCommand( "turn 1" );
                
            delay = .3
            
            if self.mobs_killed == self.mustKill:
                print("   KILLING ZOMBIES MISSION IS OVER ")
                self.agent_host.sendCommand( "turn 1" )
                self.agent_host.sendCommand( "attack 0" )
                self.state = SteveState.FORWARD

        elif self.state == SteveState.FORWARD:

            print(" FORWARD: ", nbr[self.front_of_me_idx+9])

            self.pitch0()
            
            if life < self.life :
                if self.mobs_killed == 2:               
                    self.mustKill = 3
                    self.state = SteveState.KILLING_ZOMBIES
                    self.life = life 
                    return delay
                    
            self.life = life    
                
            if nbr[self.front_of_me_idx+9] == "bedrock" and nbr[self.front_of_me_idx+18] == "air":
                print("   FORWARD: I AM JUMPING TO A HIGHER LEVEL ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "jump 1" )
                self.agent_host.sendCommand( "move 1" )
                self.agent_host.sendCommand( "turn .6" )
                delay = .23
                self.state = SteveState.TURNING2

            elif nbr[self.front_of_me_idx+9] == "bedrock" :
                print("   FORWARD: I AM TURNING AT THE CORNER ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "jump 0" )
                self.agent_host.sendCommand( "move .1" )
                self.agent_host.sendCommand( "turn .4" )
                delay = .23
                self.state = SteveState.TURNING2
                
            elif nbr[self.front_of_me_idx+9] == "red_flower" or nbr[self.front_of_me_idx] == "red_flower":
                print("   FORWARD: A red_flower IS FRONT OF ME ", nbr[self.front_of_me_idx+9])                
                self.agent_host.sendCommand( "turn 0" )
                self.prepForAttack()
                self.state = SteveState.FLOWER
                
            elif nbr[4+9] == "red_flower" or nbr[4] == "red_flower" :
                print("   FORWARD: I AM STANDING ON A red_flower ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "move 0" )
                self.agent_host.sendCommand( "turn 0" )                
                self.prepForAttack()
                self.state = SteveState.FLOWER

            elif nbr[self.front_of_me_idxl+9] == "red_flower" or nbr[self.left_of_me_idx+9] == "red_flower" or  nbr[self.behind_of_me_idxl+9] == "red_flower" or nbr[self.front_of_me_idxl] == "red_flower" or nbr[self.left_of_me_idx] == "red_flower" or  nbr[self.behind_of_me_idxl] == "red_flower":
                print("   FORWARD: A red_flower IS IN MY LEFT ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "turn -.6" )                
                self.state = SteveState.FLOWER

            elif nbr[self.front_of_me_idxr+9] == "red_flower" or nbr[self.right_of_me_idx+9] == "red_flower" or  nbr[self.behind_of_me_idxr+9] == "red_flower" or nbr[self.front_of_me_idxr] == "red_flower" or nbr[self.right_of_me_idx] == "red_flower" or  nbr[self.behind_of_me_idxr] == "red_flower":
                print("   FORWARD: A red_flower IS IN MY RIGHT ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "turn .1" )                
                self.state = SteveState.FLOWER
                
            elif nbr[self.front_of_me_idx+9] == "air" and nbr[self.front_of_me_idx] == "bedrock":
                print("   THERE IS NO OBSTACLE IN FRONT OF ME ")
                self.agent_host.sendCommand( "jump 0" )
                self.agent_host.sendCommand( "turn 0" )
                self.agent_host.sendCommand( "move 1" )
                delay = .3                                
                
            elif nbr[self.front_of_me_idx+9] == "air" and nbr[self.front_of_me_idx] == "air":
                print("   THERE IS GAP IN FRONT OF ME ")
                self.agent_host.sendCommand( "move .1" )
                self.agent_host.sendCommand( "jump 0" )
                self.agent_host.sendCommand( "turn -.4" )
                delay = .3                                
                self.state = SteveState.TURNING2
            else:
                print("   FORWARD: OOPS... ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand( "jump 1" )
                self.agent_host.sendCommand( "move .2" )


        elif self.state == SteveState.TURNING2:       
            
            self.pitch0()
            
            print("   TURNING2: ")

            if nbr[self.left_of_me_idx+9] != "bedrock":
                print("   TURNING ")
                self.agent_host.sendCommand( "turn .2" )               
            elif nbr[self.front_of_me_idx+9] != "air" :    
                print("   TURNING (redundant) ", nbr[self.front_of_me_idx+9])
                
                if self.isInTrap(nbr):
                    print("   TURNING: trap ")
                    self.agent_host.sendCommand( "jump 1" )               
                self.agent_host.sendCommand( "turn .2" )               
            else:    
                print("   TURNED ")
                self.agent_host.sendCommand( "jump 0" )               
                self.agent_host.sendCommand( "turn 0" )               
                self.state = SteveState.FORWARD

        # TODO ez előttig van csak átgondolva, itt tart a greenpill
        elif self.state == SteveState.FLOWER:                        
            
            self.pitch90()

            print(" FLOWER: ", nbr[self.front_of_me_idx+9])
            print("   FLOWER: *** attack *** ")


            if nbr[4] == "red_flower" :
                self.agent_host.sendCommand( "move .1" )                
            elif nbr[4+9] == "red_flower" :
                self.agent_host.sendCommand( "move 0" )
                self.agent_host.sendCommand( "turn 0" )                
                print("   FLOWER: attack standing on red_flower", nbr[self.front_of_me_idx+9])
                delay = .14                            
                self.state = SteveState.PICK_UP
            elif nbr[self.front_of_me_idx+9] == "red_flower" :
                self.agent_host.sendCommand( "attack 0" )
                self.agent_host.sendCommand( "move .3" )
            elif nbr[self.front_of_me_idxl+9] == "red_flower" or nbr[self.left_of_me_idx+9] == "red_flower" or  nbr[self.behind_of_me_idxl+9] == "red_flower":                
                self.agent_host.sendCommand( "attack 0" )                
                self.agent_host.sendCommand( "turn -.6" )                
            elif nbr[self.front_of_me_idxr+9] == "red_flower" or nbr[self.right_of_me_idx+9] == "red_flower" or  nbr[self.behind_of_me_idxr+9] == "red_flower":
                self.agent_host.sendCommand( "attack 0" )
                self.agent_host.sendCommand( "turn .1" )                
            elif nbr[self.front_of_me_idx] == "red_flower":                
                self.agent_host.sendCommand( "attack 0" )                
                self.agent_host.sendCommand( "move .1" )                
            elif nbr[self.front_of_me_idxl] == "red_flower" or nbr[self.left_of_me_idx] == "red_flower" or  nbr[self.behind_of_me_idxl] == "red_flower":                
                self.agent_host.sendCommand( "attack 0" )                
                self.agent_host.sendCommand( "move .1" )                
                self.agent_host.sendCommand( "turn -.6" )                
            elif nbr[self.front_of_me_idxr] == "red_flower" or nbr[self.right_of_me_idx] == "red_flower" or  nbr[self.behind_of_me_idxr] == "red_flower":
                self.agent_host.sendCommand( "move .2" )                
                self.agent_host.sendCommand( "attack 0" )
                self.agent_host.sendCommand( "turn .6" )                
                
            else:
                self.state = SteveState.FORWARD
                self.agent_host.sendCommand( "attack 0" );

        elif self.state == SteveState.PICK_UP:            
            print(" PICK_UP: ", nbr[self.front_of_me_idx+9])

            if nbr[4+9] == "red_flower":
                print("   PICK_UP: *** new attack *** ", nbr[self.front_of_me_idx+9]) 
                self.agent_host.sendCommand( "attack 1" );
            elif self.lookingat == "red_flower":
                print("   I CAN SEE A red_flower!!!!!!!!!!")
                self.agent_host.sendCommand( "move 0" );                                
                self.agent_host.sendCommand( "turn 0" );
                self.agent_host.sendCommand( "attack 1" );                
            else:
                self.state = SteveState.FLOWER
                
            if flower:    
                print("   PICK_UP: *** PICKED *** ", self.y, " #RF ", self.nof_red_flower)
                
                self.state = SteveState.FORWARD
            else:
    
                self.agent_host.sendCommand( "jump 0" );
                
                delay = .24
                print("   PICK_UP: WHAT CAN WE DO? ")
                
        else:                       
            pass
                
        return delay

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
