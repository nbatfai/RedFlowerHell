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

viragszam = 0

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
        
        self.front_of_me_idx = 0
        self.front_of_me_idxr = 0
        self.front_of_me_idxl = 0        
        self.right_of_me_idx = 0
        self.left_of_me_idx = 0
        self.balhatul = 0
        self.jobbhatul = 0
        
        self.nof_red_flower = 0
        self.lookingat = ""
        self.attackLvl = 0
        
        self.collectedFlowers = {}
        for i in range(100):
            self.collectedFlowers[i] = False

        self.collectedFlowers[1] = True
        self.collectedFlowers[2] = True

        self.viragszam = 0
        self.szeddfel = 0
        self.fordulas = 0

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
                    self.collectedFlowers[self.attackLvl] = True
                    self.agent_host.sendCommand( "look -1" )
                    time.sleep(.4)
                    if self.lvlUp(observations.get("nbr3x3", 0)):
                        return True
    def pickUp(self):
        self.agent_host.sendCommand( "attack 1" )
        time.sleep(.23)
        self.attackLvl = self.y

    def lvlUp(self, nbr):
        if self.collectedFlowers[self.y]:
            self.turnToWall(nbr)
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(.2)                
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(.2)
            return True
        else:
            return False

    def idle(self, delay):
        #print("      SLEEPING for ", delay)
        time.sleep(delay)
                                                        




################################################################################

    def calcNbrIndex(self):
        if self.yaw >= 180-22.5 and self.yaw <= 180+22.5 :
            self.front_of_me_idx = 1+9
            self.front_of_me_idxr = 2+9
            self.front_of_me_idxl = 0
            self.right_of_me_idx = 5+9
            self.left_of_me_idx = 3
            self.balhatul = 6
            self.jobbhatul = 8+9
        elif self.yaw >= 180+22.5 and self.yaw <= 270-22.5 :
            self.front_of_me_idx = 2+9
            self.front_of_me_idxr = 5+9
            self.front_of_me_idxl =1
            self.right_of_me_idx = 8+9
            self.left_of_me_idx = 0
            self.balhatul = 3
            self.jobbhatul = 7 + 9
        elif self.yaw >= 270-22.5 and self.yaw <= 270+22.5 :
            self.front_of_me_idx = 5+9
            self.front_of_me_idxr = 8+9
            self.front_of_me_idxl = 2
            self.right_of_me_idx = 7+9
            self.left_of_me_idx = 1
            self.balhatul = 0
            self.jobbhatul = 6 + 9
        elif self.yaw >= 270+22.5 and self.yaw <= 360-22.5 :
            self.front_of_me_idx = 8+9
            self.front_of_me_idxr = 7+9
            self.front_of_me_idxl = 5
            self.right_of_me_idx = 6+9
            self.left_of_me_idx = 2
            self.balhatul = 1
            self.jobbhatul = 3 + 9
        elif self.yaw >= 360-22.5 or self.yaw <= 0+22.5 :
            self.front_of_me_idx = 7+9
            self.front_of_me_idxr = 6+9
            self.front_of_me_idxl = 8
            self.right_of_me_idx = 3+9
            self.left_of_me_idx = 5
            self.balhatul = 2
            self.jobbhatul = 0 + 9
        elif self.yaw >= 0+22.5 and self.yaw <= 90-22.5 :
            self.front_of_me_idx = 6+9
            self.front_of_me_idxr = 3+9
            self.front_of_me_idxl = 7
            self.right_of_me_idx = 0+9
            self.left_of_me_idx = 8
            self.balhatul = 5
            self.jobbhatul = 1 + 9
        elif self.yaw >= 90-22.5 and self.yaw <= 90+22.5 :
            self.front_of_me_idx = 3+9
            self.front_of_me_idxr = 0+9
            self.front_of_me_idxl = 6
            self.right_of_me_idx = 1+9
            self.left_of_me_idx = 7
            self.balhatul = 8
            self.jobbhatul = 2 + 9
        elif self.yaw >= 90+22.5 and self.yaw <= 180-22.5 :
            self.front_of_me_idx = 0+9
            self.front_of_me_idxr = 1+9
            self.front_of_me_idxl = 3
            self.right_of_me_idx = 2+9
            self.left_of_me_idx = 6
            self.balhatul = 7
            self.jobbhatul = 5 + 9
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

    #Az elején felküldjük az ágenst.
    def felMegy(self):
        print("Felmegyek.")
        for i in range(0,50):
            self.agent_host.sendCommand("move 1")
            time.sleep(0.0001)
            self.agent_host.sendCommand("jumpmove 1")
            time.sleep(0.0001)
        self.agent_host.sendCommand("turn -1")
        time.sleep(0.1)
        self.agent_host.sendCommand("look 1")
        time.sleep(0.1)

    #Eleinte többször előfordult az a hiba, hogy a pálya közepe
    #felé folytatta útját Steve. Ennek kiküszöbölésére hoztuk létre 
    #ezt az egyszerű eljárást, de végül nem alkalmaztuk.
    def befeleNez(self, elotte):
        print("Hoppá. Nem szabad befelé néznem! Fordulok jobbra.")
        if (elotte == 'air'):
            self.agent_host.sendCommand("turn 1")
            time.sleep(0.1)
    #def megy(self):

    #Sarkok érzékelése. Mivel előfordulhat olyan eset, hogy Steve a 
    #saroknál belemegy egy 'gödörbe', minden fordulás előtt hátra
    #ugrik egyet.
    def sarok(self, obs0, obs1, obs2):
        if (obs0 == 'dirt' and obs1 == 'dirt' and obs2 == 'dirt'):
            print("Sarkot érzékeltem. Fordulok.")
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("turn -1")
            time.sleep(0.1)
            self.fordulas += 1


    #2 szinttel lentebb megy Steve. Kicsit kacifántosnak tűnik, de így
    #akkor sincs probléma, ha sarkoknál megy lentebb.
    def leMegy(self):
        print("Ezen a szinten már nincs értelme virágokat keresgélni. Lentebb megyek 2 szinttel.")
        for i in range(0,4):
            self.agent_host.sendCommand("strafe -1")
            time.sleep(0.01)
        for i in range(0,4):
            self.agent_host.sendCommand("move 1")
            time.sleep(0.01)
        for i in range(0,5):
            self.agent_host.sendCommand("move -1")
            time.sleep(0.01)

    #def erzekel(self):

    #Az egyik legfontosabb rész. Mindig lefut, ha a 3x3x3-as blokkban
    #virág található. Ha az érzékelés után nem látja Steve maga körül
    #a virágot, hátrébb lép, és újra meghívódik az eljárás. Így kisebb
    #az esélye annak, hogy elhagyja a virágokat a sebesség növelésekor.
    def felSzed(self, tomb, balelol, jobbelol, bal, jobb, balhatul, jobbhatul, elol, alatt):
        self.viragszam += 1
        print("Felszedem a virágot!")
        if (tomb[balelol] == 'red_flower'):
            self.agent_host.sendCommand("strafe -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("move 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe 1")
            time.sleep(0.1)
        elif (tomb[jobbelol] == 'red_flower'):
            self.agent_host.sendCommand("strafe 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("move 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe -1")
            time.sleep(0.1)
        elif (tomb[bal] == 'red_flower'):
            self.agent_host.sendCommand("strafe -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe 1")
            time.sleep(0.1)
        elif (tomb[jobb] == 'red_flower'):
            self.agent_host.sendCommand("strafe 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe -1")
            time.sleep(0.1)
        elif (tomb[balhatul] == 'red_flower'):
            self.agent_host.sendCommand("strafe -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("move -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe 1")
            time.sleep(0.1)
        elif (tomb[jobbhatul] == 'red_flower'):
            self.agent_host.sendCommand("strafe 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("move -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpstrafe 1")
            time.sleep(0.1)
        elif (tomb[elol] == 'red_flower'):
            self.agent_host.sendCommand("move 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("turn -1")
            time.sleep(0.1)
        elif (tomb[alatt] == 'red_flower'):
            self.agent_host.sendCommand("look 1")
            time.sleep(0.1)
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.4)
            self.agent_host.sendCommand("look -1")
            time.sleep(0.1)
            self.agent_host.sendCommand("jumpmove 1")
            time.sleep(0.1)
        else:
            self.viragszam -= 1
            for i in range(0,3):
                self.agent_host.sendCommand('move -1')
                time.sleep(0.0001)
            self.agent_host.sendCommand('jumpmove -1')
            time.sleep(0.0001)
            time.sleep(0.1)



    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:

        #először felmegyünk. Még a while ciklus előtt. 
        self.felMegy()
        if (self.pitch == 0):
            self.agent_host.sendCommand('look 1')
            time.sleep(0.1)

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
        #print("\r    Steve's Coords: ", self.x, self.y, self.z, end='')
        #print("    Steve's Yaw: ", self.yaw)        
        #print("    Steve's Pitch: ", self.pitch)        

        #self.checkInventory(observations)
        #print("Number of flowers: ", self.nof_red_flower)

        self.whatISee(observations)
        #print("    Steve's <): ", self.lookingat)
                        
        self.calcNbrIndex()
        #Sarokhoz értem?
        self.sarok(nbr[self.front_of_me_idxr],nbr[self.front_of_me_idxl],nbr[self.front_of_me_idx])

        #Leszedem a virágot, ha utasítást kapok.
        if (self.szeddfel != 0):
            self.felSzed(nbr, self.front_of_me_idxl, self.front_of_me_idxr, self.left_of_me_idx, self.right_of_me_idx, self.balhatul, self.jobbhatul, self.front_of_me_idx, 4)
            self.szeddfel = 0
            return True

        #Virág érzékelése a 3x3x3-as gridben. Ha van benne virág, a szeddfel változó miatt meghívódik a következő iterációban a felSzed()
        if('red_flower' in nbr):
            print("Virágot érzékeltem!")
            self.szeddfel += 1
            #Itt vissza is térünk True-val, hogy ne menjen Steve tovább.
            return True
            #self.felSzed(nbr, self.front_of_me_idxl, self.front_of_me_idxr, self.left_of_me_idx, self.right_of_me_idx)

            #self.leMegy()
            #print('Virag')

        #Ha lentebb kell menni..
        if (self.viragszam >= 2 or self.fordulas > 4 or "flowing_lava" in nbr):
            self.leMegy()
            self.viragszam = 0
            self.fordulas = 0

        else:
            #3 blokkonként lépünk előre, így a gyorsaság a 3-szorosára nő. :)
            for i in range(0,3):
                self.agent_host.sendCommand('move 1')
                time.sleep(0.0001)
            time.sleep(0.05)



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
