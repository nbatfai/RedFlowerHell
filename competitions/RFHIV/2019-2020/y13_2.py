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
missionXML_file='nb4tf4i_d4_Rudolf_hard.xml'
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
	#my_mission.removeAllCommandHandlers()
	#my_mission.allowAllDiscreteMovementCommands()
	#my_mission.allowContinuousMovementCommand("attack")


class Hourglass:
	def __init__(self, charSet):
		self.charSet = charSet
		self.index = 0
	def cursor(self):
		self.index=(self.index+1)%len(self.charSet)
		return self.charSet[self.index]

hg = Hourglass('|/-\|')



class SteveState(Enum): 
	LVL_UP = 0
	TURN = 1
	FIXTURN = 2
	FORWARD = 3
	FLOWER = 4
	PICKUP = 5
	STUCK = 6
	PREPARE = 7
	KILLING_ZOMBIES = 8
	MASTER_ROTATION = 9
	MOVE_TO_DIR = 10

	STOP = 20


class Steve:
	def __init__(self, agent_host):
		self.agent_host = agent_host
		
		self.x = 0
		self.y = 0
		self.z = 0
		self.yaw = 0
		self.pitch = 0

		self.state = SteveState.PREPARE

		self.trapc = 0
		self.lvl = 0
		self.lvlc = 0
		
		self.front_of_me_idx = 0
		self.front_of_me_idxr = 0
		self.front_of_me_idxl = 0
		self.right_of_me_idx = 0
		self.left_of_me_idx = 0
		self.behind_of_me_idx = 0
		
		self.nof_red_flower = 0

	def calcNbrIndex(self):
		if self.yaw >= 180-30 and self.yaw <= 180+30 :
			self.front_of_me_idx = 1
			self.front_of_me_idxr = 2
			self.front_of_me_idxl = 0
			self.right_of_me_idx = 5
			self.left_of_me_idx = 3
			self.behind_of_me_idx = 7
		elif self.yaw >= 270-30 and self.yaw <= 270+30 :
			self.front_of_me_idx = 5
			self.front_of_me_idxr = 8
			self.front_of_me_idxl = 2
			self.right_of_me_idx = 7
			self.left_of_me_idx = 1
			self.behind_of_me_idx = 3
		elif self.yaw >= 360-30 or self.yaw <= 0+30 :
			self.front_of_me_idx = 7
			self.front_of_me_idxr = 6
			self.front_of_me_idxl = 8
			self.right_of_me_idx = 3
			self.left_of_me_idx = 5
			self.behind_of_me_idx = 1
		elif self.yaw >= 90-30 and self.yaw <= 90+30 :
			self.front_of_me_idx = 3
			self.front_of_me_idxr = 0
			self.front_of_me_idxl = 6
			self.right_of_me_idx = 1
			self.left_of_me_idx = 7
			self.behind_of_me_idx = 5
		else:
			print("Something is wrong, I can feel it!")

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

	def idle(self, delay):
		time.sleep(delay)
	
	
	def whatISee(self, observations):
		self.lookingat = "NOTHING"
		if "LineOfSight" in observations:
			lineOfSight = observations["LineOfSight"]
			self.lookingat = lineOfSight["type"]

	def PickUp():
		if nbr[self.front_of_me_idx+9] == "bedrock"  and nbr[self.behind_of_me_idx+9] == "bedrock" :
			self.agent_host.sendCommand( "attack 0" )
			self.Stuck()
		else :
			self.agent_host.sendCommand( "strafe -1" )
			self.agent_host.sendCommand( "move -1" )
			time.sleep(.07)
			self.agent_host.sendCommand( "strafe 0" )
			self.agent_host.sendCommand( "move 0" )
			self.Flower()
 


	def run(self):
		world_state = self.agent_host.getWorldState()
		# Loop until mission ends:
		while world_state.is_mission_running:
			delay = self.action(world_state)
			self.idle(delay)			
			world_state = self.agent_host.getWorldState()

	def action(self, world_state):
		for error in world_state.errors:
			print("Error:", error.text)
		
		if world_state.number_of_observations_since_last_state == 0:
	
			return False
		
		input = world_state.observations[-1].text
		observations = json.loads(input)
		nbr = observations.get("nbr3x3", 0)
		
		self.whatMyPos(observations)
		print("\n>>> nb4tf4i arena --- (there are observations) -------------------")
		print("Steve's Coords: ", self.x, self.y, self.z, " Yaw: ", self.yaw, " Pitch: ", self.pitch, " #RF: ", self.nof_red_flower)

		self.whatISee(observations)
		#print("	Steve's <): ", self.lookingat)
		self.calcNbrIndex()
		delay = .02
		kills = observations.get("MobsKilled", 0)
		print("Kills: ", kills)

		if self.state == SteveState.PREPARE :
			self.agent_host.sendCommand( "move -1" )
			self.agent_host.sendCommand( "turn -1" )
			time.sleep(.25)
			self.agent_host.sendCommand( "turn 0" )
			time.sleep(2.5)
			self.agent_host.sendCommand( "move 0" )
			self.agent_host.sendCommand( "hotbar.3 1" )
			self.state = SteveState.KILLING_ZOMBIES

		elif self.state == SteveState.KILLING_ZOMBIES :
			if self.lookingat == "Zombie" :
				self.agent_host.sendCommand( "turn 0" )
				print("OH, EGY ZOMBI..")
				self.agent_host.sendCommand( "attack 1" )
				time.sleep(.5)		
				self.agent_host.sendCommand( "attack 0" )
				delay = .01
			if kills >= 2 :
				self.agent_host.sendCommand( "turn 0" )
				self.state = SteveState.MASTER_ROTATION



		elif self.state == SteveState.MASTER_ROTATION :
			if self.yaw > 85 and self.yaw <= 95 :
				print("YAW:  ", self.yaw)
				time.sleep(.02)
				self.agent_host.sendCommand( "turn 0" )
				time.sleep(0.5)
				self.agent_host.sendCommand( "strafe -1" )
				if nbr[self.left_of_me_idx+9] == "bedrock" :
					self.agent_host.sendCommand( "strafe 1" )
					time.sleep(.5)
					self.agent_host.sendCommand( "strafe 0" )
					self.state = SteveState.LVL_UP
			else :
				self.agent_host.sendCommand( "turn .1" ) 
				delay = .01

		elif self.state == SteveState.LVL_UP :
			if nbr[self.front_of_me_idx+18] != "bedrock" :
				self.agent_host.sendCommand( "move 1" )
				self.agent_host.sendCommand( "jump 1" )
			else :
				self.agent_host.sendCommand( "jump 0" )
				self.idle(3)
				self.agent_host.sendCommand( "move 0" )
				self.agent_host.sendCommand( "strafe 1" )
				self.idle(0.25)
				self.agent_host.sendCommand( "strafe 0" )
				self.agent_host.sendCommand( "turn -1" ) 
				time.sleep(.5)
				self.agent_host.sendCommand( "turn 0" )
				time.sleep(.5)
				if self.y <= 12 :
					self.agent_host.sendCommand( "move 1" )
					self.agent_host.sendCommand( "jump 1" )
				else :
					self.agent_host.sendCommand( "jump 0" )
					self.agent_host.sendCommand( "move 0" )
					self.idle(1)
					self.state = SteveState.TURN

		elif self.state == SteveState.TURN :
			self.agent_host.sendCommand( "turn 1" ) 
			time.sleep(.5)
			self.agent_host.sendCommand( "turn 0" )
			time.sleep(.5)
			self.state = SteveState.FIXTURN

		elif self.state == SteveState.FIXTURN :
			if self.yaw >= 45 and self.yaw <= 135 :
				if self.yaw < 80 :
					self.agent_host.sendCommand( "turn 0.2" )
					delay = .01
				else :
					self.agent_host.sendCommand( "turn 0" )
					self.state = SteveState.FORWARD
			elif self.yaw >= 135 and self.yaw <= 225 :
				if self.yaw < 170 :
					self.agent_host.sendCommand( "turn .2" )
					delay = .01
				else :
					self.agent_host.sendCommand( "turn 0" )
					self.state = SteveState.FORWARD
			elif self.yaw >= 225 and self.yaw <= 315 :
				if self.yaw < 260 :
					self.agent_host.sendCommand( "turn 0.2" )
					delay = .01
				else :
					self.agent_host.sendCommand( "turn 0" )
					self.state = SteveState.FORWARD
			else :
				if self.yaw > 350 or self.yaw < 10 :
					self.agent_host.sendCommand( "turn 0" )
					self.state = SteveState.FORWARD
				else :
					self.agent_host.sendCommand( "turn 0.2" )
					delay = .01

		elif self.state == SteveState.FORWARD :
			self.agent_host.sendCommand( "move 0" )

			if nbr[4] == "grass" :
				self.agent_host.sendCommand( "move -1" )
				time.sleep(.18)
				self.agent_host.sendCommand( "move 0" )
				print("VIRAAAG")
				self.state = SteveState.FLOWER

			elif nbr[self.front_of_me_idx+9] == "bedrock" :
				if nbr[self.right_of_me_idx+9] == "bedrock" :
					self.state = SteveState.STUCK
				else :
					self.agent_host.sendCommand( "move 0" )
					self.state = SteveState.TURN
					time.sleep(.5)
			else :
				self.agent_host.sendCommand( "move 1" )
			delay = .01

		elif self.state == SteveState.FLOWER :
			if nbr[4] != "grass":	
				self.state = SteveState.PICKUP
			else :
				self.agent_host.sendCommand( "move 0" )
				self.agent_host.sendCommand( "pitch 1" )
				self.agent_host.sendCommand( "attack 1" )
				time.sleep(1.3)
				self.state = SteveState.PICKUP

		elif self.state == SteveState.PICKUP :
			if nbr[self.front_of_me_idx+9] == "bedrock"  and nbr[self.behind_of_me_idx+9] == "bedrock" :
				self.agent_host.sendCommand( "attack 0" )
				self.state = SteveState.STUCK
			else :
				self.agent_host.sendCommand( "strafe -1" )
				self.agent_host.sendCommand( "move -1" )
				time.sleep(.07)
				self.agent_host.sendCommand( "strafe 0" )
				self.agent_host.sendCommand( "move 0" )
				self.state = SteveState.FLOWER

		elif self.state == SteveState.STUCK :
			self.agent_host.sendCommand( "move 1" )
			time.sleep(0.4)
			self.agent_host.sendCommand( "jump 1" )
			time.sleep(.3)
			self.agent_host.sendCommand( "jump 0" )
			self.agent_host.sendCommand( "move 0" )
			self.state = SteveState.FORWARD

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
	print("Number of flowers: "+ str(steve.nof_red_flower))

print("Mission ended")
# Mission has ended.


