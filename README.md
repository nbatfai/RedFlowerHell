Red Flower Hell in Minecraft MALMÖ
==================================
NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena
--------------------------------------------------------------------------

* HI agents: [initial hack](https://youtu.be/SQSoLiRM1MQ): 18,  [world record](https://youtu.be/8yLmkjc2OiI): 46 poppies
* SW agents: [initial hack](https://youtu.be/WaXQtsc1tHQ): 13, world record: - poppies
* AI agents: there are no such agents at this moment, initial hack: -, world record: - poppies
* AGI agents: there are no such agents at this moment, initial hack: -, world record: - poppies

# Red Flower Hell
Nowadays the key players in the artificial intelligence industry have their own platform for AGI research that is typically built on some well-known current or former game title. For example, Google uses the [Quake III Arena](https://github.com/deepmind/lab) and [Star Craft II](https://github.com/deepmind/pysc2).
Microsoft uses [Minecraft](https://www.microsoft.com/en-us/research/project/project-malmo/) for similar research purpose [1].

The [Project MALMÖ](https://github.com/Microsoft/malmo) is a Minecraft mod created by the Microsoft. Now we have started to use MALMÖ in education of programming. Then based on the experience gained with this we would like to use it in AGI research too. For this purpose we have begun to experiment with our own series of competitions called **Red Flower Hell**. The specific purpose of this challenge series is to collect as many red flowers as possible before the lava flows down the hillside as it can be seen in the following figure. ![Red Flower Hell Arena](RFHarena.png "Red Flower Hell Arena")

## Human Intelligence agents (HI agents)
In the elements of Red Flower Hell series we are going to develop intelligent agents to collect poppies. After this we would also like develop AGI agents in this environment. It is therefore essential to know that how many poppies can a human player collect?

[nb4tf4i.xml](nb4tf4i.xml)  
[nb4tf4i_red_flower_hell_basic_human.py](nb4tf4i_red_flower_hell_basic_human.py)

HI agents Results

* [initial hack](https://youtu.be/SQSoLiRM1MQ): 18, N. Bátfai
* [world record](https://youtu.be/8yLmkjc2OiI): 46 poppies, I. Horváth

## Software agents (SW agents)
These programs do not contain the usual MI solutions (such as graph searching or Q-learning), but only naive heuristic algorithms.

### Family circle (with my children)

The first experiments with MALMÖ  we had taken in our immediate family circle as we did with, for example,  project [BrainB](https://www.twitch.tv/videos/139186614) [1] or [SMNIST](https://youtu.be/-tSRwJgVpJk) [2]. We have played  [with](https://youtu.be/bAPSu3Rndi8) cheating (using ObservationFromGrid) and [without](https://youtu.be/x52iPOwwMn4) cheating as well.



### Study circles (for primary and secondary school pupils and students)

#### First circle
[Demo](https://youtu.be/uA6RHzXH840)  

[nb4tf4i.xml](nb4tf4i.xml)  
[nb4tf4i_red_flower_hell_basic.py](nb4tf4i_red_flower_hell_basic.py)

* Modify the initial loop
```python
# Loop until mission ends:
while world_state.is_mission_running:
    print("--- nb4tf4i arena -----------------------------------\n")
    self.agent_host.sendCommand( "move 1" )
    time.sleep(.5)            
    self.agent_host.sendCommand( "turn 1" )
    time.sleep(.5)
    world_state = self.agent_host.getWorldState()
```
to rotate Steve at half speed.
* Modify the loop to move Steve forward and backward.
* Modify the loop to move Steve forward by turning right and left (zig-zag).
* Modify the loop to walk Steve
around in the arena.
* Modify the loop to move up Steve
in spiral line in the arena until he reach the lava.

#### Second circle
[Demo](https://youtu.be/Fc33ByQ6mh8)  

[nb4tf4i_d.xml](nb4tf4i_d.xml)  
[nb4tf4i_red_flower_hell_basic_d.py](nb4tf4i_red_flower_hell_basic_d.py)

```python
# Loop until mission ends:
while world_state.is_mission_running:
    print("--- nb4tf4i arena -----------------------------------\n")
    self.agent_host.sendCommand( "move 1" )
    time.sleep(.5)            
    self.agent_host.sendCommand( "move 1" )
    time.sleep(.5)            
    self.agent_host.sendCommand( "move 1" )
    time.sleep(.5)            
    self.agent_host.sendCommand( "turn 1" )
    time.sleep(.5)
    world_state = self.agent_host.getWorldState()
```

Let's do the same task as in the first circle but now with using [discrete motion commands](https://microsoft.github.io/malmo/0.17.0/Schemas/MissionHandlers.html#type_DiscreteMovementCommand).

#### Third circle
[Programming task](https://youtu.be/-GX8dzGqTdM)  
[nb4tf4i_red_flower_hell_basic_d_sense.py](nb4tf4i_red_flower_hell_basic_d_sense.py)

```python
class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.x = 0
        self.y = 0
        self.z = 0        
        self.yaw = 0
        self.pitch = 0        

    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:
        while world_state.is_mission_running:
            print("--- nb4tf4i arena -----------------------------------\n")
            if world_state.number_of_observations_since_last_state != 0:

                sensations = world_state.observations[-1].text
                print("    sensations: ", sensations)                
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)
                print("    3x3x3 neighborhood of Steve: ", nbr3x3x3)

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

                print("    Steve's Coords: ", self.x, self.y, self.z)        
                print("    Steve's Yaw: ", self.yaw)        
                print("    Steve's Pitch: ", self.pitch)
```

* Modify this code to print what Steve sees.

Hint:   
```python
if "LineOfSight" in observations:
    lineOfSight = observations["LineOfSight"]
    self.lookingat = lineOfSight["type"]
print("    Steve's <): ", self.lookingat)
```
* Then modify the code further to print a debug message if Steve sees a red flower.  
A solution can be seen in this video: https://youtu.be/mT9FOzzSjUI

* Finally, modify the code to mine a red flower.

#### Fourth circle

[Programming task](https://youtu.be/I6n8acZoyoo): Steve should go up to the lava then come back down to the starting level walking ahead of the lava.

#### Fifth circle

Let's do the same task as in the previous circle but now with using 5x5x5 or 7x7x7 grid of blocks in ObservationFromGrid.

### Courses (for university students)
In these courses students can earn extra points by solving MALMÖ based programming tasks.

#### High-level programming languages I
[Syllabus](http://smartcity.inf.unideb.hu/~norbi/P1/SillabuszProg1.pdf), [lectures](https://arato.inf.unideb.hu/batfai.norbert/UDPROG/deprecated/), [laboratory work](https://gitlab.com/nbatfai/bhax/-/tree/master/thematic_tutorials/bhax_textbook_IgyNeveldaProgramozod), [community](https://www.facebook.com/groups/udprog/).

![Norbi Prog1](NorbiProg1.jpg "Norbi Prog1")  
There are usually roughly 130 students in the High-level programming languages I lecture. This picture was taken on Wed, 19 Feb 2020.

The purpose of the following contests (Red Flower Hell I.-IV.) is to gain experience in agent programming. There is no reward or prize. We play the game for the game's sake.

##### Red Flower Hell I.

10 Feb - 2 Mar   
Using ObservationFromGrid has already been a cheating in itself. But in this first round there are no rules, anything is allowed, for example the students can use directly the coordinates of flowers from mission XML file with the teleport command... and so on.

How to participate? Comment the link of your YouTube video to the post: https://www.facebook.com/groups/udprog/permalink/1337108209810398/

Results
* [initial hack](https://youtu.be/WaXQtsc1tHQ): 13 poppies, Bátfai, N. (without AbsoluteMovementCommand)
* first place: 58 poppies, there was a dead heat for first place between [Pusztai, R.](https://youtu.be/_yIQe9iiaL4) (with trivial teleporting), [Hajdu, B.](https://youtu.be/VPrzLiI8_oU) (with using water), [Nagy, V.](https://youtu.be/UWRm2iQGiC0), [Kusmiczki, B. & Nagy, E.](https://youtu.be/RPvSv5jmzho), [Bence, C. & Barna, B.](https://youtu.be/JD4-sZ9BqGw), [Kálny, Z. & Szilágy Z.](https://youtu.be/2TU8KTtcNr4), [Salánki, L. & Kovács, I.](https://youtu.be/-Y_aFPxT4Nw), [Nagy, L. E. & Tódor, G.](https://youtu.be/GgpDeO4GUdA), [Takács, B.](https://youtu.be/kLaV9kENU2s), [Szabó, B. & Pete, B.](https://youtu.be/TcBYAAp4Og0), [Hosszú, Sz.](https://youtu.be/0gXwCGaJCyc), [Semendi, Á.](https://youtu.be/E4VIvq39FZE) and [Béres, M.](https://youtu.be/dbhrMjtxXgM) (with trivial teleporting)
* [second place](https://youtu.be/FFswEcKiC2s): 57, Kántor, D.
* third place: -

Summary: the purpose of this round was to install and learn about MALMÖ.

##### Red Flower Hell II.

2 Mar - 23 Mar  

Based on experience gained in the first round, the following are prohibited:
* using the data of the mission XML file
* using [absolute movement commands](https://microsoft.github.io/malmo/0.17.0/Schemas/MissionHandlers.html#type_AbsoluteMovementCommand)
* modifying the mission XML file
* changing the game mode
* gaining mouse control

How to participate? Comment the link of your YouTube video to the post: https://www.facebook.com/groups/udprog/permalink/1342653805922505/

Results
* [initial hack](https://youtu.be/g_nWTXByPbs): 14 poppies, Bátfai, N.
* current first place: 39 poppies, [Hajdu, B.](https://youtu.be/0W_Oaxg2uyg) 
* current second place: 37 poppies, [Káplár, I. et al.](https://youtu.be/ul70t9PZLrc) 
* current third place: 24 poppies, [Bátfai, N.](https://youtu.be/sH4nlNheNf4)
* current 4-th place: 23 poppies, [Kántor, D.](https://youtu.be/6hb-MaX2OAE) 
* current 5-th place: 21 poppies, [Hajdu, B. & György, D.](https://youtu.be/22t7Jhanl8Q)
* current 6-th place: 17 poppies, [Olasz, Zs. & Ignácz, M.](https://youtu.be/shMWqpyP8QU)

##### Red Flower Hell III.

23 Mar - 6 Apr

Qualification limit: 14 poppies. The deadline for submission of the source code of your SF agent is 1 Apr. There will be online qualifiers followed by offline finals  at the spring school holidays. Until now the red flowers have always been placed to the same place.
In the finals, the locations of the red flowers will be re-generated. (For example, try this mission XML file: [nb4tf4i_d_2.xml](nb4tf4i_d_2.xml) )

Results
* initial hack: -
* current first place: -
* current second place: -
* current third place: -  

##### Red Flower Hell IV.

6 Apr - 13 Apr

In this round the full arena will be re-generated: not only the coords of the red flowers but also the walls of the hillside will change as it can be seen in the following figure.

![Red Flower Hell Arena 3](RFHarena3.png "Red Flower Hell Arena 3")

Results
* initial hack: -
* current first place: -
* current second place: -
* current third place: -  

#### High-level programming languages II
See AI agents

#### Esport
See AGI agents


## Artificial Intelligence agents (AI agents)


## Artificial General Intelligence agents (AGI agents)

## Our other Minecraft-based activities

* [Szolon Hackerei - Esport és Programozás Verseny](http://smartcity.inf.unideb.hu/~norbi/DEACH/DEACHMinecraft005.pdf)
* [„Debrecen a kockák origójában” - a DEAC-Hackers esport szakosztály Minecrafttal kapcsolatos koncepciója ](http://smartcity.inf.unideb.hu/~norbi/NB4tf4iRedFlowerHell/DEACH_BN_template4_2-toborzo-MC2-verseny-nb4tf4ai-pipacs.pdf)

# References

[1] Johnson, M., Hofmann, K., Hutton, T.,Bignell, D. (2016). The Malmo Platform for Artificial Intelligence Experimentation, 25th International Joint Conference on Artificial Intelligence, https://www.ijcai.org/Proceedings/16/Papers/643.pdf

[2] Bátfai, N., Papp, D., Besenczi, R., Bogacsovics, G., & Veres, D. (2019). Benchmarking Cognitive Abilities of the Brain with the Event of Losing the Character in Computer Games. Studia Universitatis Babeș-Bolyai Informatica, 64(1), 15-25. doi:10.24193/subbi.2019.1.02

[3] Norbert Bátfai, Dávid Papp, Gergő Bogacsovics, Máté Szabó, Viktor Szilárd Simkó, Márió Bersenszki, Gergely Szabó, Lajos Kovács, Ferencz Kovács, Erik Szilveszter Varga (2019). Object file system software experiments about the notion of number in humans and machines. Cognition, Brain, Behavior. An interdisciplinary journal. Volume XXIII, Nr 4, 257-280, doi:10.24193/cbb.2019.23.15

[4] Bátfai,  N., Csukonyi Cs., Papp D, Hermann Cs., Deákné O. E.,
Győri K. (2020) The DEAC-Hackers esport department's education and research concept in AI in Minecraft (accepted Hungarian manuscript)

___
Norbert Bátfai, PhD., University of Debrecen, IT Dept.,  batfai.norbert@inf.unideb.hu  
[nb4tf4i](http://mine.ly/nb4tf4i.1)

Last modified: Tue, 3 Mar 2020 21:18:00 GMT
