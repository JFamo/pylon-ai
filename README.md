# Pylon
## A StarCraft II Artificial Intelligence

## Dependencies
This repository uses the python-sc2 api client library [https://github.com/Dentosal/python-sc2] and is built using Python 3.7.0 with StarCraft II Client 4.11.3 from Blizzard Entertainment

## How It Works
Pylon runs primarily based on a weighted queue implementation. His linked list tracks an intended build order while asynchronous methods assess his needs and push units/buildings to the queue. These nodes are ranked by importance and built as they are dequeued. 

Pylon's genetic algorithm adjusts these weights as heuristics of importance and additionally considers factors such as the frequency of pylon building, number of gateways per expansion, and supply ratio of various unit types to form varying army compositions. I plan to implement the neural network outlined on [pythonprogramming.net] for placement and scouting.
