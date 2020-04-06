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
missionXML_file='nb4tf4i_d_2.xml'
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
        self.pitch = 90

        
        self.first_turn = True
    
        self.front_of_me_idx = 0
        self.front_of_me_idxr = 0
        self.front_of_me_idxl = 0
        self.right_of_me_idx = 0
        self.left_of_me_idx = 0
        self.back_of_me_idx = 0

        self.level = False
        self.index = abs(self.y-26)
        self.teszt = 0

        self.nof_red_flower = 0
        self.lookingat = ""
        self.attackLvl = 0

        self.collectedFlowers = {}
        for i in range(100):
            self.collectedFlowers[i] = False


    def checkInventory(self, observations):
        for i in range(2):
            hotbari = 'Hotbar_'+str(i)+'_item'
            hotbars = 'Hotbar_'+str(i)+'_size'
            slot0_contents = observations.get(hotbari, "")
            if slot0_contents == "red_flower":
                slot0_size = observations.get(hotbars, "")
                if self.nof_red_flower < slot0_size :
                    self.nof_red_flower = slot0_size
                    print("            A RED FLOWER IS MINED AND PICKED UP")
                    print("            Steve's lvl: ", self.y, "Flower lvl: ", self.attackLvl)
                    self.collectedFlowers[self.y] = True
                    
                    if self.lvlDown(observations.get("nbr3x3", 0)):
                        return True



    def pickUp(self):
        self.agent_host.sendCommand( "attack 1" )
        time.sleep(.5)
        self.agent_host.sendCommand( " jumpmove -1")

        self.attackLvl = self.y

    def lvlDown(self, nbr):
        if self.collectedFlowers[self.y] == True:
            if self.isInTrap(nbr):
                self.exit(nbr)
            print("megy a ciklus")
            if nbr[self.left_of_me_idx] == "air":
                self.agent_host.sendCommand("strafe -1")
                time.sleep(.1)
                return True

            if nbr[self.right_of_me_idx+9] == "dirt":

                print("---------------------------------------------------")
                self.agent_host.sendCommand("strafe -1")
                

    
                time.sleep(.1)
                
                return True

            elif nbr[self.right_of_me_idx] == "air" and self.attackLvl == self.y:
                self.agent_host.sendCommand("strafe 1")
                time.sleep(.2)
                return True

            elif nbr[self.left_of_me_idx+9] == "dirt" and self.attackLvl == self.y:

                print("---------------------------------------------------")
                
                self.agent_host.sendCommand("strafe 1")

                time.sleep(.2)
                #self.teszt-1
                return True
            elif nbr[self.front_of_me_idx] == "air":
                	self.agent_host.sendCommand("move 1")
                	return True

            elif nbr[self.back_of_me_idx] == "air":
                	self.agent_host.sendCommand("move -1")
                	time.sleep(.1)
                	return True
        else:
            print("=/=/=/=/=/=/=/=/=/=/=/=/")
            return False

    def idle(self, delay):
        #print("      SLEEPING for ", delay)
        time.sleep(delay)

    def isInTrap(self, nbr):

        dc = 0
        nbri = [9,10,11,12,14,15,16,17]
        for i in range(1, len(nbri)):
            if nbr[nbri[i]]=="dirt" :
                dc = dc + 1
        return dc > 5

    def exit(self, nbr):

        if nbr[self.front_of_me_idx+18] == "dirt" or nbr[self.back_of_me_idx+18] == "red_flower":
            
            self.agent_host.sendCommand( "jumpmove -1" )
            time.sleep(.08)

        elif nbr[self.front_of_me_idx+9] == "air":
        	self.agent_host.sendCommand("jumpmove 1")
        	time.sleep(.1)
        	self.agent_host.sendCommand("jumpmove 1")
        	time.sleep(.1)

        else:
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(.1)


    def turnFromWall(self, nbr):
        if (nbr[self.right_of_me_idx+9]=="air" and nbr[self.left_of_me_idx+9]=="dirt") or (nbr[self.right_of_me_idx]=="air" and nbr[self.left_of_me_idx]=="dirt"):
            self.agent_host.sendCommand( "turn 1" )
            time.sleep(.1)
        else:
            self.agent_host.sendCommand( "turn -1" )
            time.sleep(.1)

    def turnToWall(self, nbr):
        if (nbr[self.right_of_me_idx+9]=="air" and nbr[self.left_of_me_idx+9]=="dirt") or (nbr[self.right_of_me_idx]=="air" and nbr[self.left_of_me_idx]=="dirt"):
            self.agent_host.sendCommand( "turn -1" )
            time.sleep(.2)
        else:
            self.agent_host.sendCommand( "turn 1" )
            time.sleep(.2)

    def calcNbrIndex(self):
        if self.yaw >= 180-22.5 and self.yaw <= 180+22.5 :
            self.front_of_me_idx = 1
            self.front_of_me_idxr = 2
            self.front_of_me_idxl = 0
            self.right_of_me_idx = 5
            self.left_of_me_idx = 3
            self.back_of_me_idx = 7
        elif self.yaw >= 180+22.5 and self.yaw <= 270-22.5 :
            self.front_of_me_idx = 2
            self.front_of_me_idxr = 5
            self.front_of_me_idxl =1
            self.right_of_me_idx = 8
            self.left_of_me_idx = 0
            self.back_of_me_idx = 6
        elif self.yaw >= 270-22.5 and self.yaw <= 270+22.5 :
            self.front_of_me_idx = 5
            self.front_of_me_idxr = 8
            self.front_of_me_idxl = 2
            self.right_of_me_idx = 7
            self.left_of_me_idx = 1
            self.back_of_me_idx = 3
        elif self.yaw >= 270+22.5 and self.yaw <= 360-22.5 :
            self.front_of_me_idx = 8
            self.front_of_me_idxr = 7
            self.front_of_me_idxl = 5
            self.right_of_me_idx = 6
            self.left_of_me_idx = 2
            self.back_of_me_idx = 0
        elif self.yaw >= 360-22.5 or self.yaw <= 0+22.5 :
            self.front_of_me_idx = 7
            self.front_of_me_idxr = 6
            self.front_of_me_idxl = 8
            self.right_of_me_idx = 3
            self.left_of_me_idx = 5
            self.back_of_me_idx = 1
        elif self.yaw >= 0+22.5 and self.yaw <= 90-22.5 :
            self.front_of_me_idx = 6
            self.front_of_me_idxr = 3
            self.front_of_me_idxl = 7
            self.right_of_me_idx = 0
            self.left_of_me_idx = 8
            self.back_of_me_idx = 2
        elif self.yaw >= 90-22.5 and self.yaw <= 90+22.5 :
            self.front_of_me_idx = 3
            self.front_of_me_idxr = 0
            self.front_of_me_idxl = 6
            self.right_of_me_idx = 1
            self.left_of_me_idx = 7
            self.back_of_me_idx = 5
        elif self.yaw >= 90+22.5 and self.yaw <= 180-22.5 :
            self.front_of_me_idx = 0
            self.front_of_me_idxr = 1
            self.front_of_me_idxl = 3
            self.right_of_me_idx = 2
            self.left_of_me_idx = 6
            self.back_of_me_idx = 8
        else:
            print("There is great disturbance in the Force...")



    def corner(self, nbr):
        if nbr[self.back_of_me_idx] == "dirt" and nbr[self.right_of_me_idx] == "dirt" and nbr[0] == "air":
            return True
        else: 
            return False




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

    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:
        while world_state.is_mission_running:

            #print(">>> nb4tf4i arena -----------------------------------\n")
            act = self.action(world_state)
            #print("nb4tf4i arena >>> -----------------------------------\n")
            if not act:
                self.idle(.017)
            world_state = self.agent_host.getWorldState()

    def action(self, world_state):
        for error in world_state.errors:
            print("Error:", error.text)

        if world_state.number_of_observations_since_last_state == 0:
          
            return False

        input = world_state.observations[-1].text
        observations = json.loads(input)
        nbr = observations.get("nbr3x3", 0)
        #print(observations)

        self.whatMyPos(observations)
        print("\r    Steve's Coords: ", self.x, self.y, self.z, end='')


        self.checkInventory(observations)
  

        self.whatISee(observations)
   

        self.calcNbrIndex()

        if self.isInTrap(nbr):
            time.sleep(.01)
            print("CSAPDABAN VAGYOKKKKKKKKKKKKKKKKKKk")
            self.exit(nbr)
            return True

 


        if self.y < 32 and self.level == False:
            self.agent_host.sendCommand( "jumpmove 1" )
            return True
        else:
            self.level = True

 
        if self.first_turn == True and self.y == 32:
            self.agent_host.sendCommand("turn 1")
            time.sleep(.1)
            self.agent_host.sendCommand("look 1")
            self.agent_host.sendCommand("look 1")
            self.first_turn = False




        if self.level == True :


            for i in range(9):
                if nbr[i+9]=="red_flower":
                    print("        I CAN SEE A RED FLOWER: ", i, " LEVEL ", self.y)
                    if i == self.front_of_me_idx :
                        print("F            A RED FLOWER IS RIGTH IN FRONT OF ME")
                        self.agent_host.sendCommand( "move 1" )
                        time.sleep(.15)
                        #self.agent_host.sendCommand( "look 1" )
                        #time.sleep(.2)
                        print("Steve <) ", self.lookingat)
                        return True
                    elif i == self.front_of_me_idxr :
                        print("R            A RED FLOWER IS RIGTH IN RIGHT OF ME")
                        self.agent_host.sendCommand( "strafe 1" )
                        time.sleep(.2)
                        return True
                    elif i == self.front_of_me_idxl :
                        print("L            A RED FLOWER IS RIGTH IN LEFT OF ME")
                        self.agent_host.sendCommand( "strafe -1" )
                        time.sleep(.2)
                        return True
                    elif i == 4  :
                        self.red_flower_is_mining = True
                        print("            I AM STANDING ON A RED FLOWER!!!")

                
                        print("ATTACK            I AM STANDING ON A RED FLOWER!!! LEVEL ", self.y)
                        self.pickUp()
                            
                        return True
                    elif i == self.left_of_me_idx:
                        self.agent_host.sendCommand("strafe -1")
                        print("balos virag")
                        time.sleep(.2)
                        return True

                    elif i == self.right_of_me_idx:
                        self.agent_host.sendCommand("strafe 1")
                        print("jobbos virag")
                        time.sleep(.2)
                        return True

                    else :
                        print("            I AM TURNING TO A RED FLOWER")
                        self.agent_host.sendCommand( "move -1" )
                        time.sleep(.2)
                        return True

   

        if self.lvlDown(nbr):
            print("        LVL DOWN")

        if nbr[self.front_of_me_idx+9] == "dirt" and self.isInTrap(nbr) == False:
            self.agent_host.sendCommand("turn 1")
            time.sleep(.15)


        else:

            if self.y == self.attackLvl:
                if nbr[self.left_of_me_idx] == "air":
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    return True

                if nbr[self.right_of_me_idx+9] == "dirt":

                    print("---------------------------------------------------")
                    self.agent_host.sendCommand("strafe -1")
 
                    time.sleep(.1)
               
                    return True

                elif nbr[self.right_of_me_idx] == "air":
                    self.agent_host.sendCommand("strafe 1")
                    time.sleep(.1)
                    return True

                elif nbr[self.left_of_me_idx+9] == "dirt":

                    print("---------------------------------------------------")
                
                    self.agent_host.sendCommand("strafe 1")
          
                    time.sleep(.1)
             
                    return True
        
            print("        THERE IS NO OBSTACLE IN FRONT OF ME", end='')

            if nbr[self.front_of_me_idx]=="dirt" and nbr[self.front_of_me_idx+9] == "air" and self.attackLvl != self.y:
     
                self.agent_host.sendCommand( "move 1" )
                print("mek elore")
                time.sleep(.015)
             
            else:
                if nbr[self.front_of_me_idx+9] == "dirt" and nbr[self.left_of_me_idx+9] == "dirt" and self.isInTrap(nbr) == False:
                    self.agent_host.sendCommand("turn 1")
                    print("probalok jobbra")
                
                 


        return True

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
