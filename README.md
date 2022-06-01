# The Game Of Life
Two versions of Conway's Game Of Life: a C++ version (CLI) and a Python version (GUI)

## What is the Game Of Life?
Conway's Game Of Life is a 2D cellular automaton, you can find out how it works [here](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

## C++ Version
The C++ version is a CLI program. The `cpp` folder contains the main program, a folder containing some example configurations that can be loaded into the program and a log folder where will be stored the logfile, in case the user decides to save it. The grid size is fixed, modifying it you risk to break the program when, for example, importing a configuration file during the execution.

## Python Version
The Python version is a GUI program. The `py` folder contains the main program and a folder where the program icon is stored. You can modify the grid size as you wish, and can also modify the sleep time between iterations. If the grid is quite big, you can switch from a sequential execution (single-thread) to a multi-thread approach. The sleep time's maximum value is 3 seconds to avoid runtime issues related to Tkinter.
