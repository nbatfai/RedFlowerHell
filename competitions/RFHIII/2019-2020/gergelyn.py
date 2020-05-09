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
    # flush print output immediately
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
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
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n")
    print("Version history\n", "Code: Green Pill",
          sys.argv[0], ", series 24, version 3, max 28 poppies: https://youtu.be/cfhh3llDoRo, Norbert Bátfai, nbatfai@gmail.com, Nándor Bátfai.\n")
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.drawBlock(0, 0, 0, "lava")


class Hourglass:
    def __init__(self, charSet):
        self.charSet = charSet
        self.index = 0

    def cursor(self):
        self.index = (self.index+1) % len(self.charSet)
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
    BACKWARD = 8


class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host

        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0

        self.xc = 0
        self.yc = 0
        self.zc = 0

        self.state = SteveState.GOING_UP

        self.trapc = 0
        self.lvl = 0
        self.lvlc = 0

        self.front_of_me_idx = 0
        self.front_of_me_idxr = 0
        self.front_of_me_idxl = 0
        self.right_of_me_idx = 0
        self.left_of_me_idx = 0
        self.back_of_me_idx = 0

        self.nof_red_flower = 0

    def isInTrap(self, nbr):
        dc = 0
        nbri = [9, 10, 11, 12, 14, 15, 16, 17]
        for i in range(0, len(nbri)):
            if nbr[nbri[i]] == "dirt":
                dc = dc + 1
        return dc > 6

    def checkInventory(self, observations):
        flower = False
        dirt = False
        dirt_idx = 0
        for i in range(9):
            hotbari = 'Hotbar_'+str(i)+'_item'
            hotbars = 'Hotbar_'+str(i)+'_size'
            slot0_contents = observations.get(hotbari, "")
            if slot0_contents == "red_flower":
                slot0_size = observations.get(hotbars, "")
                if self.nof_red_flower < slot0_size:
                    self.nof_red_flower = slot0_size
                    print("   *** A RED FLOWER IS MINED AND PICKED UP *** ")
                    flower = True
            if slot0_contents == "dirt":
                dirt_idx = i+1
                slot0_size = observations.get(hotbars, "")
                if 0 < slot0_size:
                    dirt = True

        return flower, dirt, dirt_idx

    def idle(self, delay):
        #print("      SLEEPING for ", delay)
        time.sleep(delay)

    def isInTrap(self, nbr):
        if nbr[9] == "dirt" and nbr[10] == "dirt" and nbr[11] == "dirt" and nbr[12] == "dirt" and nbr[14] == "dirt" and nbr[15] == "dirt" and nbr[16] == "dirt" and nbr[17] == "dirt":
            return True
        else:
            return False

    def calcNbrIndex(self):
        if self.yaw >= 180-22.5 and self.yaw <= 180+22.5:
            self.front_of_me_idx = 1
            self.front_of_me_idxr = 2
            self.front_of_me_idxl = 0
            self.right_of_me_idx = 5
            self.left_of_me_idx = 3
            self.back_of_me_idx = 7
        elif self.yaw >= 180+22.5 and self.yaw <= 270-22.5:
            self.front_of_me_idx = 2
            self.front_of_me_idxr = 5
            self.front_of_me_idxl = 1
            self.right_of_me_idx = 8
            self.left_of_me_idx = 0
            self.back_of_me_idx = 6
        elif self.yaw >= 270-22.5 and self.yaw <= 270+22.5:
            self.front_of_me_idx = 5
            self.front_of_me_idxr = 8
            self.front_of_me_idxl = 2
            self.right_of_me_idx = 7
            self.left_of_me_idx = 1
            self.back_of_me_idx = 3
        elif self.yaw >= 270+22.5 and self.yaw <= 360-22.5:
            self.front_of_me_idx = 8
            self.front_of_me_idxr = 7
            self.front_of_me_idxl = 5
            self.right_of_me_idx = 6
            self.left_of_me_idx = 2
            self.back_of_me_idx = 0
        elif self.yaw >= 360-22.5 or self.yaw <= 0+22.5:
            self.front_of_me_idx = 7
            self.front_of_me_idxr = 6
            self.front_of_me_idxl = 8
            self.right_of_me_idx = 3
            self.left_of_me_idx = 5
            self.back_of_me_idx = 1
        elif self.yaw >= 0+22.5 and self.yaw <= 90-22.5:
            self.front_of_me_idx = 6
            self.front_of_me_idxr = 3
            self.front_of_me_idxl = 7
            self.right_of_me_idx = 0
            self.left_of_me_idx = 8
            self.back_of_me_idx = 2
        elif self.yaw >= 90-22.5 and self.yaw <= 90+22.5:
            self.front_of_me_idx = 3
            self.front_of_me_idxr = 0
            self.front_of_me_idxl = 6
            self.right_of_me_idx = 1
            self.left_of_me_idx = 7
            self.back_of_me_idx = 5
        elif self.yaw >= 90+22.5 and self.yaw <= 180-22.5:
            self.front_of_me_idx = 0
            self.front_of_me_idxr = 1
            self.front_of_me_idxl = 3
            self.right_of_me_idx = 2
            self.left_of_me_idx = 6
            self.back_of_me_idx = 8
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
        if self.pitch != 90:
            self.agent_host.sendCommand("look 1")
            self.agent_host.sendCommand("look 1")
            delay = .07

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
        # print(observations)

        self.whatMyPos(observations)
        print("\n>>> nb4tf4i arena --- (there are observations) -------------------")
        print("Steve's Coords: ", self.x, self.y, self.z, " Yaw: ",
              self.yaw, " Pitch: ", self.pitch, " #RF: ", self.nof_red_flower)

        flower, dirt, dirt_idx = self.checkInventory(observations)
        #print("Number of flowers: ", self.nof_red_flower)

        self.whatISee(observations)
        #print("    Steve's <): ", self.lookingat)

        self.calcNbrIndex()

        delay = .02

        if self.state == SteveState.GOING_UP:

            print(" GOING_UP: ", nbr[self.front_of_me_idx+9])

            if self.y <= 31:
                self.agent_host.sendCommand("jumpmove 1")
                print("   GOING_UP: jumpmove 1 ", nbr[self.front_of_me_idx+9])
            else:
                print("   GOING_UP: turn 1 28<=y ",
                      nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand("turn 1")
                delay = .13
                #self.state = SteveState.FIRST_TURN
                self.state = SteveState.BACKWARD

        elif self.state == SteveState.BACKWARD:
            print("BACKWARD: ", nbr[self.front_of_me_idx+9])
            if self.pitch != 45:
                self.agent_host.sendCommand("look 1")
                delay = .1
            if nbr[self.left_of_me_idx+9] == "dirt" and nbr[self.right_of_me_idx+9] == "dirt":
                self.agent_host.sendCommand("turn 1")
                print("I turned")
                delay = .1
                self.agent_host.sendCommand("jumpmove 1")
                print("I jumpmoved")
                delay = .1
                self.agent_host.sendCommand("move 1")
                print("I jumpmoved")
                delay = .1
                self.state = SteveState.FIRST_TURN
            elif nbr[self.back_of_me_idx+9] == "air" or nbr[self.back_of_me_idx+9] == "red_flower":
                self.agent_host.sendCommand("attack 1")
                delay = .1
                self.agent_host.sendCommand("move -1")
                delay = .1
            else:
                self.agent_host.sendCommand("turn -1")
                delay = .1

        elif self.state == SteveState.FIRST_TURN:
            if self.pitch == 90:
                self.agent_host.sendCommand("look -1")
                self.agent_host.sendCommand("look -1")
            elif self.pitch == 45:
                self.agent_host.sendCommand("look -1")
            else:
                print("Ugy nezek ki, mint aki benez")
            print(" FIRST_TURN: ", nbr[self.front_of_me_idx+9])
            self.agent_host.sendCommand("turn -1")
            delay = .1
            self.state = SteveState.FORWARD

        elif self.state == SteveState.FORWARD:

            print(" FORWARD: ", nbr[self.front_of_me_idx+9])
            if self.pitch == 90:
                self.agent_host.sendCommand("look -1")
                self.agent_host.sendCommand("look -1")
            elif self.pitch == 45:
                self.agent_host.sendCommand("look -1")
            else:
                print("Ugy nezek ki, mint aki benez")
            if self.isInTrap(nbr):
                print("   FORWARD: trap")
                self.agent_host.sendCommand("jumpmove 1")

            # and nbr[self.front_of_me_idx] == "dirt":
            if nbr[self.front_of_me_idx+9] == "air":
                self.agent_host.sendCommand("move 1")
                print("   FORWARD: move 1 ", nbr[self.front_of_me_idx+9])

            elif nbr[self.left_of_me_idx+9] == "dirt" and nbr[self.right_of_me_idx+9] == "dirt":
                self.agent_host.sendCommand("turn 1")
                print("I turned")
                delay = .1
                self.agent_host.sendCommand("jumpmove 1")
                print("I jumpmoved")
                delay = .1
                self.agent_host.sendCommand("move 1")
                print("I jumpmoved")
                delay = .1

            elif nbr[self.front_of_me_idx+9] == "dirt":
                print("   FORWARD: turn 1 ", nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand("turn 1")
                delay = .1
                self.state = SteveState.TURNING

            elif nbr[self.front_of_me_idx+9] == "red_flower":
                print("   FORWARD: front of me red_flower look ",
                      nbr[self.front_of_me_idx+9])
                self.prepForAttack()
                self.state = SteveState.FLOWER

            elif nbr[4+9] == "red_flower":
                print("   FORWARD: standing on red_flower look ",
                      nbr[self.front_of_me_idx+9])
                self.prepForAttack()
                self.state = SteveState.FLOWER
            else:
                print(" Hoppá ")
                pass

        elif self.state == SteveState.TURNING:

            print(" TURNING: ", nbr[self.front_of_me_idx+9])
            if self.isInTrap(nbr):
                print("   TURNING: trap ")
                self.agent_host.sendCommand("jumpmove 1")

            if nbr[self.front_of_me_idx+9] == "air" or nbr[self.front_of_me_idx+9] == "air":
                self.state = SteveState.FORWARD
            elif nbr[self.front_of_me_idx+9] == "dirt":
                self.state = SteveState.FORWARD
            elif nbr[self.front_of_me_idx+9] == "red_flower":
                print("   TURNING: red_flower tamadasra felkeszul",
                      nbr[self.front_of_me_idx+9])
                self.prepForAttack()
                self.agent_host.sendCommand("move 1")
                self.state = SteveState.FLOWER
            else:
                pass

        # TODO ez előttig van csak átgondolva, itt tart a greenpill
        elif self.state == SteveState.FLOWER:

            print(" FLOWER: ", nbr[self.front_of_me_idx+9])
            print("   FLOWER: *** attack *** ")
            self.agent_host.sendCommand("attack 1")
            self.lvl = self.y
            delay = .23

            self.state = SteveState.PICK_UP

        elif self.state == SteveState.PICK_UP:
            print(" PICK_UP: ", nbr[self.front_of_me_idx+9])

            if nbr[self.front_of_me_idx+9] == "red_flower":
                print("   PICK_UP: *** new attack *** ",
                      nbr[self.front_of_me_idx+9])
                self.agent_host.sendCommand("jump 1")
                self.agent_host.sendCommand("attack 1")
                delay = .23
            elif nbr[self.back_of_me_idx+9] == "red_flower":
                print("     PICK_UP: *** new attack behind me *** ",
                      nbr[self.back_of_me_idx+9])
                self.agent_host.sendCommand("jumpmove -1")
                delay = .23
                self.agent_host.sendCommand("attack 1")
                delay = .23
            if self.isInTrap(nbr):
                print("   PICK_UP: trap ")
                if self.trapc < 1:
                    print("   PICK_UP: trap if")
                    self.agent_host.sendCommand("jumpmove -1")
                    self.agent_host.sendCommand("jumpmove -1")
                    self.trapc = self.trapc + 1
                else:
                    print("   PICK_UP: trap else")
                    self.agent_host.sendCommand("jumpmove 1")
                    self.agent_host.sendCommand("jumpmove 1")

                    self.trapc = 0
                    delay = .25

            else:
                self.trapc = 0
                self.state = SteveState.FORWARD

            if flower:
                print("   PICK_UP: *** PICKED *** ",
                      self.y, " #RF ", self.nof_red_flower)

                if self.pitch != 0:
                    self.agent_host.sendCommand("look -1")
                    self.agent_host.sendCommand("look -1")

#                self.lvl = self.y
                self.state = SteveState.LVL_DOWN
            else:
                self.state = SteveState.PICK_UP
                #self.agent_host.sendCommand("move 1")

                #delay = .24
                #print("   PICK_UP: WHAT CAN WE DO? ")

        elif self.state == SteveState.LVL_DOWN:
            delay = .14

            print(" LVL_DOWN: ",
                  nbr[self.front_of_me_idx+9], " ", self.lvl, " ", self.y)

            if self.isInTrap(nbr):
                print("   LVL_DOWN: trap ")
                if nbr[self.front_of_me_idx+18] == "dirt" and nbr[self.left_of_me_idx+18] == "dirt":
                    print("      LVL_DOWN: trap elotte 2x dirt")
                    self.agent_host.sendCommand("turn 1")
                self.agent_host.sendCommand("jumpmove 1")

            else:

                if self.lvl != self.y + 1:
                    print(" LVL_DOWN: turn move turn ",
                          nbr[self.front_of_me_idx+9])
                    if self.lvlc < 2:
                        print("   LVL_DOWN: lvlc if")
                        self.agent_host.sendCommand("move 1")
                        self.agent_host.sendCommand("move 1")
                        self.agent_host.sendCommand("strafe 1")
                        self.agent_host.sendCommand("strafe 1")
                        delay = .2
                        self.lvlc = self.lvlc + 1
                    else:
                        print("   LVL_DOWN: lvlc else")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("move -1")
                        self.agent_host.sendCommand("strafe 1")
                        self.agent_host.sendCommand("strafe 1")
                        delay = .2
                        self.lvlc = 0

                else:
                    self.lvlc = 0
                    print("   LVL_DOWN: not trap ")
                    self.state = SteveState.FIRST_TURN

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
    print("   Waiting for the mission to start")
    world_state = agent_host.getWorldState()

    while not world_state.has_mission_begun:
        print("\r"+hg.cursor(), end="")
        time.sleep(0.15)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    print("NB4tf4i Red Flower Hell running\n")
    steve = Steve(agent_host)
    steve.run()
    print("Number of flowers: " + str(steve.nof_red_flower))
    time.sleep(3)

print("Mission ended")
# Mission has ended.
