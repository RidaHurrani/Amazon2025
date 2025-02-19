from src.DriveInterface import DriveInterface
from src.Constants import DriveMove, SensorData
from src.Utils import manhattan_dist_2D
from typing import List, Tuple
import heapq

class YourAgent(DriveInterface):

    def __init__(self, drive_id: int):
        """
        Constructor for YourAgent

        Arguments:
        game_id -- a unique value passed to the player drive, you do not have to do anything with it, but will have access.
        """
        self.drive_id = drive_id
        self.path: List[Tuple[int, int]] = []
        self.current_target_pod = None  # Pod we're targeting (for pickup/drop)
        self.collected_pods = set()     # Delivered pod IDs
        self.carrying_pod_id = None     # ID of the pod we're carrying

    def find_shortest_path(self, start: Tuple[int, int], goals: List[List[int]],
                          sensor_data: dict) -> List[Tuple[int, int]]:
        """
        Finds the shortest path from a starting position to the nearest goal using the A* search algorithm
        with collision avoidance.

        This method considers obstacles (walls, other drives, and pods) and applies penalties for moving
        close to other drives. It dynamically selects the nearest goal from a list of possible destinations
        and terminates once a goal is reached.

        Args:
            start (Tuple[int, int]): The starting position as (x, y) coordinates.
            goals (List[List[int]]): A list of possible goal positions, each represented as [x, y]. Can be a list
            only contain one goal
            sensor_data (dict): A dictionary containing environmental data, including:
                - FIELD_BOUNDARIES: Set of coordinates representing walls.
                - DRIVE_LOCATIONS: List of other drives' positions.
                - REAL_TIME_POD_LOCATIONS: Set of pod locations (if carrying a pod, these act as obstacles).

        Returns:
            List[Tuple[int, int]]: The shortest path from `start` to the nearest goal, represented
            as a list of (x, y) coordinates. Returns an empty list if no valid path is found.

        Behavior:
            - Converts goals into tuples for efficient lookup.
            - Uses a priority queue (min-heap) to explore paths in order of lowest cost.
            - Accounts for obstacles (walls, other drives, and pods if carrying one).
            - Applies a penalty for moving near other drives to encourage safer paths.
            - Stops searching once the closest goal is reached.
        """
        if not goals:
            return []
        goal_tuples = [tuple(goal) for goal in goals]
        walls = set(tuple(wall) for wall in sensor_data[SensorData.FIELD_BOUNDARIES])
        pods = set(tuple(pod) for pod in sensor_data[SensorData.REAL_TIME_POD_LOCATIONS])
        queue = [(0, 0, start, [start])]
        visited = set()

        while queue:
            f, g, current, path = heapq.heappop(queue)
            if current in visited:
                continue
            if current in goal_tuples:
                return path
            visited.add(current)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if (next_pos not in walls and
                    (not self.is_carrying_pod(sensor_data) or next_pos not in pods) and
                    next_pos not in visited):
                    new_g = g + 1
                    new_h = min(manhattan_dist_2D(list(next_pos), list(goal)) for goal in goal_tuples)
                    heapq.heappush(queue, (new_g + new_h, new_g, next_pos, path + [next_pos]))
        return []

    # This is the main function the simulator will call each turn
    def get_next_move(self, sensor_data: dict) -> DriveMove:
        """
        Main function for YourAgent. The simulator will call this function each loop of the simulation to see what your agent's
        next move would be. You will have access to data about the field, your robot's location, other robots' locations and more
        in the sensor_data dict argument.

        Arguments:
        sensor_data -- a dict with state information about other objects in the game. The structure of sensor_data is shown below:
            sensor_data = {
                SensorData.FIELD_BOUNDARIES: [[-1, -1], [-1, 0], ...],
                SensorData.DRIVE_LOCATIONS: [[x1, y1], [x2, y2], ...],
                SensorData.POD_LOCATIONS: [[x1, y1], [x2, y2], ...],
                SensorData.PLAYER_LOCATION: [x, y],
                SensorData.GOAL_LOCATIONS: [[x1, y1], [x2, y2], ...],  # List of goal locations
                SensorData.DRIVE_LIFTED_POD_PAIRS: [[drive_id_1, pod_id_1], [drive_id_2, pod_id_2], ...], # List of drivers id to the pod id
                SensorData.POD_TARGET_GOALS: [Pod1, Pod2, ...] # List of pod object
            }

        Returns:
        DriveMove - return value must be one of the enum values in the DriveMove class:
            DriveMove.NONE – Do nothing
            DriveMove.UP – Move 1 tile up (positive y direction)
            DriveMove.DOWN – Move 1 tile down (negative y direction)
            DriveMove.RIGHT – Move 1 tile right (positive x direction)
            DriveMove.LEFT – Move 1 tile left (negative x direction)

            DriveMove.LIFT_POD – If a pod is in the same tile, pick it up. The pod will now move with the drive until it is dropped
            DriveMove.DROP_POD – If a pod is in the same tile, drop it. The pod will now stay in this position until it is picked up
        """
        return DriveMove.NONE


