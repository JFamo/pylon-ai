# Pylon
## A StarCraft II Artificial Intelligence

## Dependencies
This repository uses the [python-sc2 api client library](https://github.com/Dentosal/python-sc2) and is built using Python 3.7.0 with StarCraft II Client 4.11.3 from Blizzard Entertainment

## How It Works
Pylon runs primarily based on a weighted queue implementation. His linked list tracks an intended build order while asynchronous methods assess his needs and push units/buildings to the queue. These nodes are ranked by importance and built as they are dequeued. 

Pylon's genetic algorithm adjusts these weights as heuristics of importance and additionally considers factors such as the frequency of pylon building, number of gateways per expansion, and supply ratio of various unit types to form varying army compositions. His population is culled to individuals above a score of 25,000. During the selection phase individuals' scores are used as their relative probability of breeding. Only victorious or particularly high-scoring individuals are considered fit and committed after a game.

## Instructions (Windows)
Install StarCraft II at [https://starcraft2.com/en-us/](https://starcraft2.com/en-us/)

Install python from [https://www.python.org/downloads/](https://www.python.org/downloads/). Pylon is tested and developed with 3.7.0. run 

In command line, run `pip install sc2`

Download the most recent version of this repository from the master branch

Unzip the Ladder2019Season3.zip file into the `Maps` folder of your StarCraft II install location

In `controller.py`, replace 
```python
run_game(maps.get(random_map()), [
			Bot(Race.Protoss, this_pylon),
			Computer(random_race(), Difficulty.Hard)
		], realtime=False)
```
with
```python
run_game(maps.get(random_map()), [
		Human(Race.Terran),
		Bot(Race.Protoss, this_pylon)
	], realtime=True)
```

Change race with either `Human(Race.Terran)`, `Human(Race.Zerg)`, or `Human(Race.Protoss)`

Navigate to your pylon-ai install directory in command line and run `python controller.py`
