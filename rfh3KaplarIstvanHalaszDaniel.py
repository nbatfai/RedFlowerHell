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
# 2020.04.05, Káplár István

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
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print('ERROR:', e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

# -- set up the mission -- #

missionXML_file = 'nb4tf4i_d_2.xml'
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    print(
        "The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print(
        "Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.drawBlock(0, 0, 0, "lava")


class Hourglass:
    def __init__(self, charSet):
        self.charSet = charSet
        self.index = 0

    def cursor(self):
        self.index = (self.index + 1) % len(self.charSet)
        return self.charSet[self.index]


hg = Hourglass('|/-\|')
#classon belul hogy? pls
turn_count = 0
class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.turncount = 0
        self.egyetle=False
        self.kettotle=False
        self.hotbar=True
        self.poppy = 0
        self.poppyack = 0
        self.poppycheck = False
        self.try_bool= True
        self.koorig_count=0

    def simanfel(self, ut):
        self.agent_host.sendCommand("turn 1")
        self.agent_host.sendCommand("turn 1")
        self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("move 1")

        roadfel = 0
        while (roadfel < ut):
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("jumpmove 1")
            roadfel += 1
            time.sleep(.1)      #.2   .05
        #self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("turn -1")
        time.sleep(.01)     #.2

    def lavaig(self):
        lavatour=True
        """roadfel = 0
        while(roadfel < 48):
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("jumpmove 1")
            roadfel += 1
            """
        masodik_ell=True
        while lavatour:
            world_state = self.agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state != 0:
                sensations = world_state.observations[-1].text
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)
                # print("    3x3x3 neighborhood of Steve: ", nbr3x3x3)
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
                # print("    Steve's Coords: ", self.x, self.y, self.z)
                # print("    Steve's Yaw: ", self.yaw)
                # print("    Steve's Pitch: ", self.pitch)
                if ("flowing_lava" in nbr3x3x3 ):
                    lavatour = False
                    masodik_ell=False
                    self.agent_host.sendCommand("move -1")
                    self.agent_host.sendCommand("move -1")
                    self.agent_host.sendCommand("turn 1")
            if (lavatour):
                self.agent_host.sendCommand("move 1")
                self.agent_host.sendCommand("jumpmove 1")
            time.sleep(.05)  # .05
            if masodik_ell:
                world_state = self.agent_host.getWorldState()
                if world_state.number_of_observations_since_last_state != 0:
                    sensations = world_state.observations[-1].text
                    observations = json.loads(sensations)
                    nbr3x3x3 = observations.get("nbr3x3", 0)
                    # print("    3x3x3 neighborhood of Steve: ", nbr3x3x3)
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

                    if ("flowing_lava" in nbr3x3x3 ):
                        lavatour = False
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("turn 1")
                    if (lavatour):
                        self.agent_host.sendCommand("move 1")
                        self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(.05)  # .05


    def lavatol_vissza(self,emelet):
        self.agent_host.sendCommand("turn 1")
        akt_emelet=0
        while akt_emelet<emelet:
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            time.sleep(.01)
            akt_emelet+=1
        time.sleep(.01)
        self.agent_host.sendCommand("move -1")
        self.agent_host.sendCommand("move -1")
        time.sleep(.01)
        self.agent_host.sendCommand("turn 1")
        #print(self.yaw)
        time.sleep(.01)

    def is_lava(self,nbr3x3x3):
        if "flowing_lava" in nbr3x3x3:
            if(self.kettotle):
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")
            else:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("strafe -1")

            self.kettotle=False
            time.sleep(.1)

    def hunavirag(self, je, j, jh, be, b, bh, e, nbr3x3x3):
        if nbr3x3x3[je]== "red_flower":
            self.right_flower(nbr3x3x3,1)
            self.turncount = 0
        if nbr3x3x3[j] == "red_flower":
            self.right_flower(nbr3x3x3,0)
            self.turncount = 0
        if nbr3x3x3[jh] == "red_flower":
            self.right_flower(nbr3x3x3,-1)
            self.turncount = 0
        if nbr3x3x3[be] == "red_flower":
            self.left_flower(nbr3x3x3,1)
        if nbr3x3x3[b] == "red_flower":
            self.left_flower(nbr3x3x3,0)
        if nbr3x3x3[bh] == "red_flower":
            self.left_flower(nbr3x3x3,-1)
        if nbr3x3x3[13] == "red_flower":
            self.center_flower(0)
            self.turncount = 0
        if nbr3x3x3[e] == "red_flower":
            self.center_flower(1)
            self.turncount = 0

    def is_flower(self, nbr3x3x3):
        if(self.yaw==0):
            self.hunavirag(15,12,9,8,5,2,16,nbr3x3x3)
        elif(self.yaw==90):
            self.hunavirag(9,10,11,6,7,8,12,nbr3x3x3)
        elif(self.yaw==180):
            self.hunavirag(11,14,17,0,3,6,10,nbr3x3x3)
        else:
            self.hunavirag(17,16,15,2,1,0,14,nbr3x3x3)

    def right_flower(self,nbr3x3x3,mezo):
        if ((nbr3x3x3[10] != "dirt" and self.yaw == 180) or (nbr3x3x3[12] != "dirt" and self.yaw == 90) or (nbr3x3x3[14] != "dirt" and self.yaw == 270) or (nbr3x3x3[16] != "dirt" and self.yaw == 0)):
            if mezo == 1:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            elif mezo == -1:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            else:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            time.sleep(.1)
        self.agent_host.sendCommand("strafe 1")
        time.sleep(.1)    #.05
        steve.get_flower()

        world_state = self.agent_host.getWorldState()
        while world_state.number_of_observations_since_last_state == 0:
            world_state = self.agent_host.getWorldState()
            pass
        sensations = world_state.observations[-1].text
        observations = json.loads(sensations)
        hotbar0 = ""
        hotbar1=""
        if "Hotbar_0_variant" in observations:
            hotbar0 = observations["Hotbar_0_variant"]
        if hotbar0 != "poppy" and self.hotbar:
            if "Hotbar_1_size" in observations:
                self.poppy = observations["Hotbar_1_size"]

        else:
            if "Hotbar_1_size" in observations:
                self.poppy = observations["Hotbar_0_size"]
        self.hotbar = False

        self.poppyack+=1
        print(self.poppy)
        print(self.poppyack)

        if(self.poppy != self.poppyack):
            self.try_again()
        if mezo == 1:
            self.agent_host.sendCommand("move -1")
        elif mezo == -1:
            self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("strafe -1")
        if self.kettotle:
            #print("kettotle")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            #self.agent_host.sendCommand("strafe -1")
            time.sleep(.05)  #.1
            self.kettotle=False
        else:
            #print("egyetle")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            time.sleep(.05)    #.1
            self.kettotle=False
        world_state = self.agent_host.getWorldState()
        while world_state.number_of_observations_since_last_state == 0:
            world_state = self.agent_host.getWorldState()
            pass
        sensations = world_state.observations[-1].text
        # print("    sensations: ", sensations)
        observations = json.loads(sensations)
        nbr3x3x3 = observations.get("nbr3x3", 0)

    def left_flower(self, nbr3x3x3, mezo):
        if ((nbr3x3x3[10] != "dirt" and self.yaw == 180) or (nbr3x3x3[12] != "dirt" and self.yaw == 90) or (
                nbr3x3x3[14] != "dirt" and self.yaw == 270) or (nbr3x3x3[16] != "dirt" and self.yaw == 0)):
            if mezo == 1:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            elif mezo == -1:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            else:
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
                self.agent_host.sendCommand("move -1")
            time.sleep(.1)  # .1

        self.agent_host.sendCommand("strafe -1")
        time.sleep(.1)  # .1
        steve.get_flower()
        self.poppyack+=1
        if mezo == 1:
            self.agent_host.sendCommand("move -1")
        elif mezo == -1:
            self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("jumpstrafe 1")
        time.sleep(.05)  # .1
        self.kettotle = True

    def center_flower(self, mezo):
        if mezo == -1:
            self.agent_host.sendCommand("move -1")
        if mezo == 1:
            self.agent_host.sendCommand("move 1")
        steve.get_flower()
        self.poppyack+=1
        if self.kettotle:
            # print("kettotle")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            # self.agent_host.sendCommand("strafe -1")
            time.sleep(.05)  # .1
            self.kettotle = False
        else:
            # print("egyetle")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("strafe -1")
            time.sleep(.05)  # .1
            self.kettotle = False

    def is_wall(self, nbr3x3x3):
        world_state = self.agent_host.getWorldState()

        if (self.yaw == 0):
            if (nbr3x3x3[15] == "dirt" and nbr3x3x3[16] == "dirt" and nbr3x3x3[17] == "dirt"):  # elotte fal
                if (self.turncount <= 8 or self.kettotle == False): #4
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("turn -1")
                    time.sleep(.05)
                    self.turncount += 1
                else:
                    if self.kettotle:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        print("kettotle")
                    else:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        print("egyetle")
                    time.sleep(.1)
                    self.turncount = 0
                    # print("lentebb")

        elif (self.yaw == 270):
            if (nbr3x3x3[11] == "dirt" and nbr3x3x3[14] == "dirt" and nbr3x3x3[17] == "dirt"):  # elotte fal
                if (self.turncount <= 8 or self.kettotle == False):
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("turn -1")
                    time.sleep(.05)
                    self.turncount += 1
                else:
                    if self.kettotle:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    else:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.turncount = 0

        elif (self.yaw == 180):
            if (nbr3x3x3[9] == "dirt" and nbr3x3x3[10] == "dirt" and nbr3x3x3[11] == "dirt"):  # elotte fal
                if (self.turncount <= 8 or self.kettotle == False):
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("turn -1")
                    time.sleep(.05)
                    self.turncount += 1
                else:
                    if self.kettotle:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    else:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.turncount = 0

        else:
            if (nbr3x3x3[9] == "dirt" and nbr3x3x3[12] == "dirt" and nbr3x3x3[15] == "dirt"):  # elotte fal
                if (self.turncount <= 8 or self.kettotle == False):
                    self.agent_host.sendCommand("move -1")
                    time.sleep(.1)
                    self.agent_host.sendCommand("turn -1")
                    time.sleep(.05)
                    self.turncount += 1
                else:
                    if self.kettotle:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    else:
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe -1")
                    time.sleep(.1)
                    self.turncount = 0

    def try_again(self):
        self.agent_host.sendCommand("move -1")
        self.agent_host.sendCommand("move -1")
        self.agent_host.sendCommand("move -1")
        self.agent_host.sendCommand("move -1")
        time.sleep(.05)
        world_state = self.agent_host.getWorldState()
        self.koorig_count = -4
        while self.try_bool:
            #print("c")
            world_state = self.agent_host.getWorldState()
            time.sleep(.1)
            while world_state.number_of_observations_since_last_state == 0:
                world_state = self.agent_host.getWorldState()
                pass
            sensations = world_state.observations[-1].text
            # print("    sensations: ", sensations)
            observations = json.loads(sensations)
            nbr3x3x3 = observations.get("nbr3x3", 0)
            hotbar0 = ""
            hotbar1 = ""
            if "Hotbar_0_variant" in observations:
                hotbar0 = observations["Hotbar_0_variant"]
            if hotbar0 != "poppy" and self.hotbar:
                if "Hotbar_1_size" in observations:
                    self.poppy = observations["Hotbar_1_size"]

            else:
                if "Hotbar_0_size" in observations:
                    self.poppy = observations["Hotbar_0_size"]
            self.hotbar = False
            if self.poppy == self.poppyack or (nbr3x3x3[10] == "dirt" and self.yaw == 180) or (nbr3x3x3[12] == "dirt" and self.yaw == 90) or (
                        nbr3x3x3[14] == "dirt" and self.yaw == 270) or (nbr3x3x3[16] == "dirt" and self.yaw == 0) or self.koorig_count==3:
                self.try_bool = False
                self.poppyack = self.poppy
            else:
                self.agent_host.sendCommand("move 1")
                time.sleep(.1)
                self.koorig_count +=1
            if(nbr3x3x3[13]=="red_flower"):
                self.agent_host.sendCommand("move -1")
                time.sleep(.1)
                self.get_flower()
                print("pipacs")

        if self.koorig_count==3:
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("move -1")
            time.sleep(.1)
        elif self.koorig_count==2:
            self.agent_host.sendCommand("move -1")
            self.agent_host.sendCommand("move -1")
            time.sleep(.1)
        elif self.koorig_count==1:
            self.agent_host.sendCommand("move -1")
            time.sleep(.1)
        elif self.koorig_count==-1:
            self.agent_host.sendCommand("move 1")
            time.sleep(.1)
        elif self.koorig_count==-2:
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            time.sleep(.1)
        elif self.koorig_count== -3:
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
        elif self.koorig_count== -4:
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
            self.agent_host.sendCommand("move 1")
        self.try_bool = True

    def get_flower(self):
        print("red_flower")
        self.agent_host.sendCommand("attack 1")
        time.sleep(.3)
        world_state = self.agent_host.getWorldState()
        sensations = world_state.observations[-1].text
        observations = json.loads(sensations)
        hotbar0 = ""

        if "Hotbar_0_variant" in observations:
            hotbar0 = observations["Hotbar_0_variant"]

        if hotbar0 == "poppy" and self.hotbar:
            self.agent_host.sendCommand("hotbar.2 1")
            self.agent_host.sendCommand("hotbar.2 0")
            time.sleep(.1)
            self.hotbar = False

        self.agent_host.sendCommand("jumpuse")
        time.sleep(.1)  # .2

        time.sleep(.1)

    def move(self,nbr3x3x3):
        steve.is_lava(nbr3x3x3)
        steve.is_flower(nbr3x3x3)
        steve.is_wall(nbr3x3x3)
        self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("move 1")
        time.sleep(.013)    #0.05
        #time.sleep(.05)    #0.05


    def run(self):
        world_state = self.agent_host.getWorldState()
        #world_state = self.agent_host.peekWorldState()
        self.agent_host.sendCommand("look 1")
        self.agent_host.sendCommand("look 1")
        self.hotbar=True
        steve.lavaig()
        steve.lavatol_vissza(7)    #5
        self.agent_host.sendCommand("strafe 1")
        self.agent_host.sendCommand("strafe 1")
        self.agent_host.sendCommand("strafe -1")
        time.sleep(.01)
        while world_state.is_mission_running:
            if world_state.number_of_observations_since_last_state != 0:
                sensations = world_state.observations[-1].text
                # print("    sensations: ", sensations)
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)
                # print("\n    3x3x3 neighborhood of Steve: \n", nbr3x3x3)
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
                #print(self.yaw)
                steve.move(nbr3x3x3)
            #else:
                #print("MOREEBUUBAJLESZ")

            world_state = self.agent_host.getWorldState()




num_repeats = 1
for ii in range(num_repeats):

    my_mission_record = MalmoPython.MissionRecordSpec()

    # Attempt to start a mission:
    max_retries = 6
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_mission_record)
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
        print("\r" + hg.cursor(), end="")
        time.sleep(0.15)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    print("NB4tf4i Red Flower Hell running\n")
    steve = Steve(agent_host)
    steve.run()

print("Mission ended")
# Mission has ended.
