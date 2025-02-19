## AR Day Activity


### Overview
This code package provides a simulator for a simplified version of a 2D robotics floor. Your goal as the designer is 
to code the brain of a robot in the form of an Agent class to navigate a robot to a goal location and
pick up a Pod object and carry that to the goal.

The game is intended to only have the player's agent class modified. This can be accomplished by creating a new file 
or editing the provided YourAgent.py file in src/ and adding the Python module and class name to the 
player_agents_list.txt file in the top level directory of the project. The game can then be run from the command 
line by running `python3 main.py`.


### How to Run the Game
1. Make sure you have Python installed (preferably 3.9 or later)
   - Check with `python3 --version`
   - https://www.python.org/downloads/release/python-3115/
2. Fork the game source code ("Fork" button on top right of this GitHub page)
   - Once you created a fork in your own GitHub repository
     - On your computer, run:
     - `git clone <your_fork_repo>`
     - `cd <your_fork_repo>`
3. Install requirements:
   - Command line: `python3 -m pip install -r requirements.txt`
4. Run the game:
   - Command line: `python3 main.py`


### Game Controls
Each turn of the game, the Orchestrator will query your Agent class for the next move your robot would like to execute. 
You can control the robot by returning a value from a set of moves defined in the src.Constants.DriveMove enum. 

Possible moves are:
- DriveMove.NONE – Do nothing
- DriveMove.UP – Move 1 tile up (positive y direction)
- DriveMove.DOWN – Move 1 tile down (negative y direction)
- DriveMove.RIGHT – Move 1 tile right (positive x direction)
- DriveMove.LEFT – Move 1 tile left (negative x direction)
- DriveMove.LIFT_POD – If a pod is in the same tile, pick it up The pod will now move with the 
  drive until it is dropped
- DriveMove.DROP_POD – If a pod is in the same tile, drop it The pod will now stay in this 
  position until it is picked up

Each turn, your agent will also be provided with information about the field, the goal, and other robots. This data 
will be in the format of a sensor data dictionary with information about other game objects. Below is an example of 
the structure of this dict:


    sensor_data = {
        SensorData.FIELD_BOUNDARIES: [[-1, -1], [-1, 0], ...],
        SensorData.DRIVE_LOCATIONS: [[x1, y1], [x2, y2], ...],
        SensorData.POD_LOCATIONS: [[x1, y1], [x2, y2], ...],
        SensorData.PLAYER_LOCATION: [x, y],
        SensorData.GOAL_LOCATION: [x, y],
        SensorData.TARGET_POD_LOCATION: [x, y],
        SensorData.DRIVE_LIFTED_POD_PAIRS: [[drive_id_1, pod_id_1], [drive_id_2, pod_id_2], ...]
    }

Use this data to stay within the field, avoid collisions, and find the goal 

### Game Orchestrator Logic
In the top level directory of the game code is a file: player_agents_list.txt. The main.py function will try to run 
all levels of the game for every agent class listed in this file. Agents must be separated by a newline. If an agent 
fails a level, the remaining levels will not be run
- [TIP] To test your code faster, modify the agent list file to only have your agent
- [TIP] To test one level at a time, comment out unwanted levels in the GAME_LEVELS variable in src/GameConfig.py
- [TIP] To test your code faster, you can increase the FPS limit in src/GameConfig.py


### Game Scoring
- Each move costs 1 point
- Score is displayed in the upper left corner of the game window
- The game will timeout after 1000 turns
- Winners are those that finished all levels in the fewest amount of steps (points)
