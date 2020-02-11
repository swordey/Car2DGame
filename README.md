# Car2DGame
This is a 2D car game written in Python for AI algorithms such as Reinforcement learning or Genetic algorithm.

It is configured to be included as a submodule, so if you only checkout this repo, you need to make some modifications to make it work.

## Fun facts
* The track in the game is generated, and you can regenerate it any time
* The car has a lidar on it
* You can set the length of the lidar ray
* You can set in which angles should the car have lidar rays
* You can get the distance of the wall in each lidar ray in each state

## How to use
* You need to checkout this as a submodule
```git
[submodule "Game"]
	path = Game
	url = git@github.com:swordey/Car2DGame.git
```
* You need to override the GameWindow object
* You can copy Game/main.py to main.py
* It will have everything to control the car manually
* Using it for learning algorithms checkout my [genetic algorithm project](https://github.com/swordey/Genetic2DCarGame).

## Built With
* [Python](https://www.python.org/)
* [pyglet](http://pyglet.org/) - The cross-platform windowing and multimedia library for Python

## Authors

* **Kardos Tamás** - *Initial work* - [Swordy](https://github.com/swordey)
