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
import copy

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
missionXML_file='nb4tf4i_d_RFHIII.xml'
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
        self.nof_red_flower = 0
        time.sleep(0.1)
        self.world_state = agent_host.getWorldState()
        self.roundsAfterTurn = 0 
        if self.world_state.number_of_observations_since_last_state != 0:
            self.sensations = self.world_state.observations[-1].text
            self.observation = json.loads(self.sensations)
        self.worldtime = 0
        self.UnrotatedMatrix = [[9,10,11],[12,13,14],[15,16,17]]
        self.lent=False
        self.countTurns=0
        self.attempt = 0
        self.pA=0
        self.pB=0
        self.pC=0
        self.wrongHeightMoves=0
    def observe(self):
        time.sleep(0.01)
        self.world_state = agent_host.getWorldState()
        if self.world_state.number_of_observations_since_last_state != 0:
            self.sensations = self.world_state.observations[-1].text
            self.observation = json.loads(self.sensations)
            return
        self.observe()
        return
    def brain(self):
        self.Move = True
        self.observe()
        nbr = self.observation.get("nbr3x3",0)
        yaw = self.observation.get("Yaw",0)
        self.X=self.observation.get("XPos",0)
        self.Y=self.observation.get("YPos",0)
        self.Z=self.observation.get("ZPos",0)
        print("\rX:" + str(self.X)[0:3]+ " Y:" + str(self.Y)[0:3]+ " Z:" + str(self.Z)[0:3]+" PA:" + str(self.pA)[0:3]+" PB:"+ str(self.pB)[0:3] + " PC:"+ str(self.pC)[0:3]+ " WrongHeightMoves:" + str(self.wrongHeightMoves), end = "")
        self.Rotation(yaw)
        if self.Y<=2:
            print("\n\nSELF-DESTRUCT")
            while self.world_state.is_mission_running:
                self.observe()
                self.agent_host.sendCommand("attack 1")
                print("\rAttemps to get flowers: "+ str(steve.attempt) +" flowers picked up: "+str(steve.nof_red_flower), end="")
                time.sleep(1)
        if nbr[self.RotatedMatrix[0][1]] == "dirt" and self.roundsAfterTurn>5:
                self.agent_host.sendCommand("turn -1")
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.05)
                self.Move = False
                self.roundsAfterTurn = 0
                self.countTurns = self.countTurns+1
        if "flowing_lava" in nbr:
            for i in range(2):
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.01)
            self.countTurns=0
            return
        if "red_flower" in nbr:
            time.sleep(0.02)
            self.approach(9)
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("move -1")
            self.countTurns=0
            self.Move=False
        if self.Move:
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            self.roundsAfterTurn= self.roundsAfterTurn+1
        if self.pA==self.Y or self.pB==self.Y or self.pC==self.Y:
            self.wrongHeightMoves = self.wrongHeightMoves+1
            print(" !", end="")
        if self.countTurns>7 or self.wrongHeightMoves>5:
            self.agent_host.sendCommand("strafe -1")
            time.sleep(0.005)
            self.countTurns=0
            self.wrongHeightMoves=0
            self.lent = False
            print("\nwrong position")
    def run(self):
        self.observe()
        self.fel2(50)
        # Loop until mission ends:
        while self.world_state.is_mission_running:
            self.brain()
            time.sleep(0.025)
    def fel2(self, height):
        self.agent_host.sendCommand("strafe 1")
        self.agent_host.sendCommand("look 1")
        self.agent_host.sendCommand("look 1")
        time.sleep(0.1)
        for k in [0,1]:
            self.agent_host.sendCommand("attack 1")
            time.sleep(0.2)
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(0.1)
        i = 1
        for i in range(9):
            self.agent_host.sendCommand("move 1")
        for i in range(height):
            self.agent_host.sendCommand( "jumpmove 1" )
            time.sleep(0.01)
            self.agent_host.sendCommand("move 1")
        time.sleep(0.005)
    def pick(self):
        self.observe()
        self.Y=self.observation.get("YPos",0)
        print("felszed ")
        print("at Y=" + str(self.Y))
        self.wrongHeightMoves=0
        self.pC = self.pB
        self.pB=self.pA
        self.pA=self.Y
        self.attempt = self.attempt+1
        time.sleep(0.05)
        self.agent_host.sendCommand("attack 1")
        time.sleep(0.3)
        self.agent_host.sendCommand("jumpuse")
        time.sleep(0.2)
        self.agent_host.sendCommand("move 1")
        time.sleep(0.01)
        self.agent_host.sendCommand("move -1")
        time.sleep(0.01)
        self.agent_host.sendCommand("move -1")
        time.sleep(0.01)
        self.observe()
        hotbar1_size =0
        if "Hotbar_1_size" in self.observation:
                    hotbar1_size = self.observation.get("Hotbar_1_size",0)
                    print("Flowers at hand: ", end="")
                    print(hotbar1_size)
        if hotbar1_size > 0:
            self.nof_red_flower = hotbar1_size
        print("----")
    def keres(self, n):
        print("keres", end="-")
        time.sleep(0.04+0.05*n)
        self.observe()
        nbr = self.observation.get("nbr3x3", 0)
        if "flowing_lava" in nbr:
            self.agent_host.sendCommand("strafe -1")
            return
        if nbr[self.RotatedMatrix[1][1]] == "red_flower":
            self.pick()
            return
        if "red_flower" in nbr:
            valasz = True
            yaw = self.observation.get("Yaw",0)
            self.Rotation(yaw)
            if valasz and (nbr[self.RotatedMatrix[1][0]-9] == "red_flower" or nbr[self.RotatedMatrix[1][0]] == "red_flower"):
                print("balra")
                self.agent_host.sendCommand("strafe -1")
                valasz=False
                self.keres(n+1)
                self.agent_host.sendCommand("jumpstrafe 1")
                time.sleep(0.05)
                self.lent = True
            if valasz and nbr[self.RotatedMatrix[1][2]] == "red_flower":
                print("jobbra")
                self.agent_host.sendCommand("strafe 1")
                valasz=False
                self.keres(n+1)
                time.sleep(0.005)
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.005)
                self.agent_host.sendCommand("move -1")
                time.sleep(0.005)
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.005)
                self.agent_host.sendCommand("move -1")
                time.sleep(0.005)
                self.agent_host.sendCommand("strafe -1")
                time.sleep(0.005)
                if self.lent:
                    self.agent_host.sendCommand("move -1")
                    time.sleep(0.005)
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(0.005)
                    self.agent_host.sendCommand("move -1")
                    time.sleep(0.005)
                    self.agent_host.sendCommand("strafe -1")
                    time.sleep(0.005)
                    self.lent = False
            if valasz and "red_flower" in [nbr[self.RotatedMatrix[0][0]-9], nbr[self.RotatedMatrix[0][0]], nbr[self.RotatedMatrix[0][1]], nbr[self.RotatedMatrix[0][2]]]:
                print("elore")
                self.agent_host.sendCommand("move 1")
                valasz=False
                self.keres(n+1)
            if valasz and "red_flower" in [nbr[self.RotatedMatrix[2][0]-9],nbr[self.RotatedMatrix[2][0]], nbr[self.RotatedMatrix[2][1]], nbr[self.RotatedMatrix[2][2]]]:
                print("hatra")
                self.agent_host.sendCommand("move -1")
                valasz=False
                self.keres(n+1)
    def Rotation(self, yaw):
        n = int(yaw/90)+2
        #print(yaw)
        #print(n)
        self.RotatedMatrix = copy.deepcopy(self.UnrotatedMatrix)
        self.MatrixToRotate = copy.deepcopy(self.RotatedMatrix)
        while n>0:
            n = n-1
            self.MatrixToRotate = copy.deepcopy(self.RotatedMatrix)
            i = j = 0
            for j in [0,1,2]:
                for i in [0,1,2]:
                    self.RotatedMatrix[i][j] = self.MatrixToRotate[j][3-i-1]
    def approach(self,n):
        for i in range(0,n):
            self.observe()
            nbr = self.observation.get("nbr3x3", 0)
            if "red_flower" in nbr:
                print("\napproach "+str(i))
                self.keres(0)
                return
            self.agent_host.sendCommand("move -1")
            time.sleep(0.06)
time.sleep(1)
print("ver 14")        
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
    print("\rAttemps to get flowers: "+ str(steve.attempt) +" flowers picked up: "+str(steve.nof_red_flower))

print("Mission ended")
# Mission has ended.
