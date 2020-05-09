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
        self.pitch = 0
        
        self.front_of_me_idx = 0
        self.front_of_me_idxr = 0
        self.front_of_me_idxl = 0        
        self.right_of_me_idx = 0
        self.left_of_me_idx = 0        
        
        self.nof_red_flower = 0
        self.lookingat = ""
        self.attackLvl = 0
        
        self.collectedFlowers = {}
        for i in range(34):
            self.collectedFlowers[i] = False

        for i in range(33,100):
            self.collectedFlowers[i] = True

#        for i in range(100):
 #           print(i)
  #          print(self.collectedFlowers[i])


        self.collectedFlowers[1] = True
        self.collectedFlowers[2] = True

#        self.flower_check = []

        self.flower_is_seen = False

        self.stop = False
        self.stop_count = 0

        self.Right_Wall_block = False
        self.Right_Wall_block_count = 0

# a ciklikusság miatt nem jó a hotbar állítás mert a slot0 értéke ciklusonként változik
    def checkInventory(self, observations):
        for i in range(9):
            hotbari = 'Hotbar_'+str(i)+'_item'
            hotbars = 'Hotbar_'+str(i)+'_size'
            slot0_contents = observations.get(hotbari, "")
            if slot0_contents == "red_flower":
                slot0_size = observations.get(hotbars, "")
                if self.nof_red_flower < slot0_size :
                    self.nof_red_flower = slot0_size   
                    self.flower_is_seen = False                                         
                    print("            A RED FLOWER IS MINED AND PICKED UP")
                    print("            Steve's lvl: ", self.y, "Flower lvl: ", self.attackLvl) 
                    self.collectedFlowers[self.attackLvl] = True
#                    self.agent_host.sendCommand( "look -1" )
                    time.sleep(.1)
#                    if self.lvlUp(observations.get("nbr3x3", 0)):
                    return True
#should include a jumpmove 1 to not activate the isintrap, which would active a turnfromwall, which causes repeated tries to lvlup
# this won't cause any problem even if it goes up one lvl

#time.sleep increased, so it won't leave mined flower on the ground and go one extra lap
    def pickUp(self):
        self.stop = True
        self.attackLvl = self.y        
        self.agent_host.sendCommand( "attack 1" )
        time.sleep(.3)
        print("jump-use")
        self.agent_host.sendCommand( "jumpuse" )
        time.sleep(.1)

    def lvlUp(self, nbr):
        if self.collectedFlowers[self.y] and self.collectedFlowers[self.y+1]:
            print("LVL_down")
            print(self.y)
            print(self.collectedFlowers[self.y])
            self.turnFromWall(nbr)
            self.agent_host.sendCommand( "move 1" )
            time.sleep(.1)                
            self.agent_host.sendCommand( "move 1" )
            time.sleep(.1)
#            if self.collectedFlowers[self.y]:
 #               self.turnFromWall(nbr)
  #              self.agent_host.sendCommand( "move 1" )
   #             time.sleep(.1)                
    #            self.agent_host.sendCommand( "move 1" )
     #           time.sleep(.1)
            self.turnToWall(nbr)
            time.sleep(.1)
            return True
        elif self.collectedFlowers[self.y] and not self.collectedFlowers[self.y+1]:
            print("LVL_up")
            print(self.y)
            print(self.collectedFlowers[self.y])
            self.turnToWall(nbr)
            self.agent_host.sendCommand( "jumpmove 1" )
            print("jumped")
            time.sleep(.1)
            self.agent_host.sendCommand( "turn -1" )
            print("turned")
            time.sleep(.1)
            self.Right_Wall_block = True   
            return True
            

        else:
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
    
    def turnFromWall(self, nbr):
        if (nbr[self.right_of_me_idx+9]=="air" and nbr[self.left_of_me_idx+9]=="dirt") or (nbr[self.right_of_me_idx]=="air" and nbr[self.left_of_me_idx]=="dirt"):
            self.agent_host.sendCommand( "turn 1" )
        else:
            self.agent_host.sendCommand( "turn -1" )
        time.sleep(.1)

    def turnToWall(self, nbr):
        if (nbr[self.right_of_me_idx+9]=="air" and nbr[self.left_of_me_idx+9]=="dirt") or (nbr[self.right_of_me_idx]=="air" and nbr[self.left_of_me_idx]=="dirt"):
            self.agent_host.sendCommand( "turn -1" )
        else:
            self.agent_host.sendCommand( "turn 1" )
        time.sleep(.1)
#added behind me 
    def calcNbrIndex(self):
        if self.yaw >= 180-22.5 and self.yaw <= 180+22.5 :
            self.front_of_me_idx = 1
            self.front_of_me_idxr = 2
            self.front_of_me_idxl = 0
            self.right_of_me_idx = 5
            self.left_of_me_idx = 3    
            self.behind_me_idx = 7        
            self.brhind_me_inxr=8
            self.behind_me_idxl=6
#        elif self.yaw >= 180+22.5 and self.yaw <= 270-22.5 :
 #           self.front_of_me_idx = 2 
  #          self.front_of_me_idxr = 5
   #         self.front_of_me_idxl =1             
    #        self.right_of_me_idx = 8
     #       self.left_of_me_idx = 0        
      #      self.behind_me_idx = 6            
        elif self.yaw >= 270-22.5 and self.yaw <= 270+22.5 :
            self.front_of_me_idx = 5
            self.front_of_me_idxr = 8
            self.front_of_me_idxl = 2
            self.right_of_me_idx = 7
            self.left_of_me_idx = 1                        
            self.behind_me_idx = 3        
            self.brhind_me_inxr=6
            self.behind_me_idxl=0
#        elif self.yaw >= 270+22.5 and self.yaw <= 360-22.5 :
 #           self.front_of_me_idx = 8            
  #          self.front_of_me_idxr = 7
   #         self.front_of_me_idxl = 5          
    #        self.right_of_me_idx = 6
     #       self.left_of_me_idx = 2                        
      #       self.behind_me_idx = 0       
        elif self.yaw >= 360-22.5 or self.yaw <= 0+22.5 :
            self.front_of_me_idx = 7
            self.front_of_me_idxr = 6
            self.front_of_me_idxl = 8
            self.right_of_me_idx = 3
            self.left_of_me_idx = 5                        
            self.behind_me_idx = 1        
            self.brhind_me_inxr=0
            self.behind_me_idxl=2
#        elif self.yaw >= 0+22.5 and self.yaw <= 90-22.5 :
 #           self.front_of_me_idx = 6
  #          self.front_of_me_idxr = 3
   #         self.front_of_me_idxl = 7          
    #        self.right_of_me_idx = 0
     #       self.left_of_me_idx = 8                        
      #      self.behind_me_idx = 2        
        elif self.yaw >= 90-22.5 and self.yaw <= 90+22.5 :
            self.front_of_me_idx = 3
            self.front_of_me_idxr = 0
            self.front_of_me_idxl = 6
            self.right_of_me_idx = 1
            self.left_of_me_idx = 7                        
            self.behind_me_idx = 5        
            self.brhind_me_inxr=2
            self.behind_me_idxl=8
#        elif self.yaw >= 90+22.5 and self.yaw <= 180-22.5 :
 #           self.front_of_me_idx = 0
  #          self.front_of_me_idxr = 1
   #         self.front_of_me_idxl = 3
    #        self.right_of_me_idx = 2
     #       self.left_of_me_idx = 6                        
      #      self.behind_me_idx = 8        
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
            
    def run(self):
        world_state = self.agent_host.getWorldState()


        #just for testing,so it wont miss first commands
        time.sleep(1)


#only if dig is not used, except fot look
        self.agent_host.sendCommand( "look 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "attack 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "move 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "attack 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "move 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "jumpmove 1" )
        time.sleep(.1)


        


#        self.agent_host.sendCommand( "hotbar.2 1" )

        for i in range(8):
            self.agent_host.sendCommand( "move 1" )
            time.sleep(.05)


        for i in range(30):
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(.1)
            self.agent_host.sendCommand( "move 1" )
            time.sleep(.1)

#only there when dig is commented
        self.agent_host.sendCommand( "move -1" )
        self.agent_host.sendCommand( "look 1" )

        self.agent_host.sendCommand( "turn -1" )



        """        
        for i in range(3):
            for i in range (80):
                self.agent_host.sendCommand( "move -1" )
            time.sleep(.1)



        time.sleep(.1)
        self.agent_host.sendCommand( "turn 1" )
        time.sleep(.1)

        for i in range (15):
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.1)

        for i in range (135):
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.05)


        time.sleep(.1)
        self.agent_host.sendCommand( "turn 1" )
        time.sleep(.1)

        for i in range (150):
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.05)

        time.sleep(.1)
        self.agent_host.sendCommand( "turn 1" )
        time.sleep(.1)

        for i in range (150):
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.05)

        time.sleep(.1)
        self.agent_host.sendCommand( "turn 1" )
        time.sleep(.1)

        for i in range (150):
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "attack 1" )
            self.agent_host.sendCommand( "move -1" )
            time.sleep(.1)




        self.agent_host.sendCommand( "look 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "strafe -1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "strafe -1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "strafe -1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "jumpmove 1" )
        time.sleep(.1)
        self.agent_host.sendCommand( "move 1" )
        time.sleep(.1)

        
        """

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
            #print("    NO OBSERVATIONS NO ACTIONS")
            return False
        
        input = world_state.observations[-1].text
        observations = json.loads(input)
        nbr = observations.get("nbr3x3", 0)
        #print(observations)
        
        self.whatMyPos(observations)
        print("\r    Steve's Coords: ", self.x, self.y, self.z, end='')        
        #print("    Steve's Yaw: ", self.yaw)        
        #print("    Steve's Pitch: ", self.pitch)        

        self.checkInventory(observations)
        #print("Number of flowers: ", self.nof_red_flower)

        self.whatISee(observations)
        #print("    Steve's <): ", self.lookingat)
                        
        self.calcNbrIndex()          

        if self.Right_Wall_block:
            if self.Right_Wall_block_count == 5:
                self.Right_Wall_block = False
                self.Right_Wall_block_count = 0      
            else:        
                self.Right_Wall_block_count = self.Right_Wall_block_count +1

        if self.isInTrap(nbr) :
#modified to jumpuse
            print("trap jump-use")
            self.agent_host.sendCommand( "jumpuse" )
            time.sleep(.5)
#            self.turnFromWall(nbr)
#            self.agent_host.sendCommand( "jumpmove 1" )
#            time.sleep(.1)            
            return True

        if self.lookingat == "red_flower":
            print(" A RED FLOWER IS FOUND (lookingat)")
            self.agent_host.sendCommand( "attack 1" )
            self.attackLvl=self.y
            return True
        
        for i in range(18):
#removed i, cause it shouldn't go down until current level's flower is mined
#removed i+18, cause it can't possibly be true if nothing goes wrong
            if nbr[i]=="red_flower":
                time.sleep(.1)
                self.flower_is_seen = True
                print("        I CAN SEE A RED FLOWER: ", i, " LEVEL ", self.y)
                if i == self.front_of_me_idx+9:
                    self.stop = True
                    print("F            A RED FLOWER IS RIGTH IN FRONT OF ME")
                    time.sleep(.1)
                    self.agent_host.sendCommand( "move 1" )
#sleep increased to detect flowers even at way faster general move speed
#                    time.sleep(.2)
#                    self.agent_host.sendCommand( "look 1" )
                    print("Steve <) ", self.lookingat)
                    return True
                elif i == self.front_of_me_idxr+9:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE RIGTH IN FRONT OF ME")
                    self.agent_host.sendCommand( "strafe 1" )
#                    self.agent_host.sendCommand( "move 1" )
                    time.sleep(.1)
                    return True
                elif i == self.right_of_me_idx+9:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE RIGTH OF ME")
                    self.agent_host.sendCommand( "strafe 1" )
#                    self.agent_host.sendCommand( "move 1" )
                    time.sleep(.1)
                    return True
                elif i == self.brhind_me_inxr+9:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE RIGTH BEHIND ME")
                    self.agent_host.sendCommand( "strafe 1" )
                    self.agent_host.sendCommand( "move -1" )
                    time.sleep(.1)
                    return True
                elif i == self.front_of_me_idxl:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE LEFT IN FRONT OF ME")
                    self.agent_host.sendCommand( "strafe -1" )
                    self.agent_host.sendCommand( "strafe 1" )
                    time.sleep(.1)
#                    self.agent_host.sendCommand( "move 1" )
                    return True
                elif i == self.left_of_me_idx:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE LEFT OF ME")
                    self.agent_host.sendCommand( "strafe -1" )
                    self.agent_host.sendCommand( "strafe 1" )
                    time.sleep(.1)
                elif i == self.behind_me_idxl:
                    self.stop = True
                    print("F            A RED FLOWER IS TO THE LEFT BEHIND ME")
                    self.agent_host.sendCommand( "strafe -1" )
                    self.agent_host.sendCommand( "strafe 1" )
                    self.agent_host.sendCommand( "move -1" )
                    time.sleep(.1)
                    return True

#                    self.agent_host.sendCommand( "move 1" )
                    return True

#                elif i == self.front_of_me_idxr :
 #                   print("R            A RED FLOWER IS RIGTH IN RIGHT OF ME")
  #                  self.agent_host.sendCommand( "strafe 1" )
   #                 time.sleep(.2)
    #                return True
     #           elif i == self.front_of_me_idxl :
      #              print("L            A RED FLOWER IS RIGTH IN LEFT OF ME")
       #             self.agent_host.sendCommand( "strafe -1" )
        #            time.sleep(.2)
         #           return True
#adding another elif for one block behind me could enable detection at faster movement
                elif i == 13  :
                    self.stop = True
                    self.red_flower_is_mining = True
                    print("            I AM STANDING ON A RED FLOWER!!!")
                    
                    if self.pitch != 90:
#                        self.agent_host.sendCommand( "look 1" )
                        print("PITCH            I AM STANDING ON A RED FLOWER!!!")
                        time.sleep(.1)
                    else:
                        print("ATTACK            I AM STANDING ON A RED FLOWER!!! LEVEL ", self.y)
                        self.pickUp()
#                        self.agent_host.sendCommand( "look -1" )
                        time.sleep(.1)
                    return True
#added elif for back, so it won't turn around
                elif i == self.behind_me_idx+9:
                    print("            A RED FLOWER IS BEHIND ME")
                    self.agent_host.sendCommand( "move -1" )
                    time.sleep(.1)
#                else :
 #                   print("            I AM TURNING TO A RED FLOWER")
  #                  self.agent_host.sendCommand( "turn 1" )
   #                 time.sleep(.2)
    #                return True
  
        if self.lvlUp(nbr):
            print("        LVL UP")

        if nbr[self.front_of_me_idx+9]!="air" and nbr[self.front_of_me_idx+9]!="red_flower":
#            print("        THERE ARE OBSTACLES IN FRONT OF ME ",  nbr[self.front_of_me_idx], end='')
  
#            self.turnFromWall(nbr)
            self.agent_host.sendCommand( "turn -1" )     
            time.sleep(.2)                  
        else:
#            print("        THERE IS NO OBSTACLE IN FRONT OF ME", end='')
#reduce sleep time            
            if nbr[self.right_of_me_idx+9]=="dirt" and not self.Right_Wall_block:
                self.agent_host.sendCommand( "strafe -1" )
                print("Right_Wall")
                time.sleep(.2)
                self.Right_Wall_block = True

            elif nbr[self.left_of_me_idx+9]=="dirt":
                self.agent_host.sendCommand( "strafe 1" )
                print("Left_Wall")
                time.sleep(.1)

            if nbr[self.front_of_me_idx]=="dirt" and not self.stop: 
#                print("standard move 1")
                self.agent_host.sendCommand( "move 1" )
                time.sleep(.02)
            elif nbr[self.front_of_me_idx]=="dirt": 
                self.stop_count = self.stop_count + 1
                print(self.stop_count)
                if self.stop_count == 4:
                    self.stop = False
                    self.stop_count = 0
            elif not self.flower_is_seen:
#                self.turnFromWall(nbr)                
                self.agent_host.sendCommand( "turn 1" )   
                time.sleep(.1)       
        return True        

num_repeats = 1
for ii in range(num_repeats):

    my_mission_record = MalmoPython.MissionRecordSpec()
#increased, because my computer needs more time to start the mission
    # Attempt to start a mission:
    max_retries = 10
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