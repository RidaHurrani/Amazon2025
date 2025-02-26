from src.Pod import Pod
from src.DriveInterface import DriveInterface
from src.Constants import DriveMove, SensorData
from src.Utils import manhattan_dist_2D
from typing import List, Optional, Tuple
import heapq


class YourAgent(DriveInterface):

    def __init__(self, drive_id: int):
        """
        Constructor for YourAgent
        """
        self.drive_id = drive_id
        self.path: List[Tuple[int, int]] = []

        # Pod we're targeting (for pickup/drop)
        # None if we don't have a target
        self.current_target_pod: Optional[Pod] = None

        # Delivered pod IDs
        self.collected_pods = set()

        # ID of the pod we're carrying
        # None if we are not currently carrying a pod
        self.carrying_pod_id: Optional[int] = None

    def is_carrying_pod(self, sensor_data: dict) -> bool:
        """Check if we're carrying a pod"""
        return any(
            pair[0] == self.drive_id
            for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS]
        )

    def find_shortest_path(
        self, start: Tuple[int, int], goals: List[List[int]], sensor_data: dict
    ) -> List[Tuple[int, int]]:
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
                SensorData.REAL_TIME_POD_LOCATIONS: [[x1, y1], [x2, y2], ...],
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

        # player_x, player_y = sensor_data[SensorData.PLAYER_LOCATION]
        # player_pos = (player_x, player_y)

        # self.carrying_pod_id = next(
        #     (pair[1] for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS] if pair[0] == self.drive_id), 
        #     None
        # )

        # # self.carrying_pod_id = None
        # # for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS]:
        # #     if pair[0] == self.drive_id:
        # #         self.carrying_pod_id = pair[1]
        # #         break

        # carrying_pod = self.carrying_pod_id is not None

        # if carrying_pod:
        #     goals = sensor_data[SensorData.GOAL_LOCATIONS]
        #     path = self.find_shortest_path(player_pos, goals, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         # self.carrying_pod_id = NONE

        #         return DriveMove.DROP_POD
        # else:
        #     pods = sensor_data[SensorData.REAL_TIME_POD_LOCATIONS]

        #     if not pods:
        #         return DriveMove.NONE  # No more pods to collect

        #     path = self.find_shortest_path(player_pos, pods, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         return DriveMove.LIFT_POD

        # if len(path) > 1:
        #     next_x, next_y = path[1] 
        #     if next_x > player_x:
        #         return DriveMove.RIGHT
        #     elif next_x < player_x:
        #         return DriveMove.LEFT
        #     elif next_y > player_y:
        #         return DriveMove.UP
        #     elif next_y < player_y:
        #         return DriveMove.DOWN

        # return DriveMove.NONE


        # player_x, player_y = sensor_data[SensorData.PLAYER_LOCATION]
        # player_pos = (player_x, player_y)

        # self.carrying_pod_id = next(
        #     (pair[1] for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS] if pair[0] == self.drive_id), 
        #     None
        # )

        # carrying_pod = self.carrying_pod_id is not None

        # if carrying_pod:
        #     goals = sensor_data[SensorData.GOAL_LOCATIONS]
        #     path = self.find_shortest_path(player_pos, goals, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         self.collected_pods.add(self.carrying_pod_id)
        #         self.carrying_pod_id = NONE
        #         return DriveMove.DROP_POD
        # else:
        #     # pods = sensor_data[SensorData.REAL_TIME_POD_LOCATIONS]
        #     pods = [pod for pod in sensor_data[SensorData.REAL_TIME_POD_LOCATIONS] if pod[0] not in self.collected_pods]

        #     if not pods:
        #         return DriveMove.NONE  # No more pods to collect

        #     path = self.find_shortest_path(player_pos, pods, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         self.carrying_pod_id = sensor_data[SensorData.REAL_TIME_POD_LOCATIONS][pods.index(path[0])][0]
        #         return DriveMove.LIFT_POD

        # if len(path) > 1:
        #     next_x, next_y = path[1] 
        #     if next_x > player_x:
        #         return DriveMove.RIGHT
        #     elif next_x < player_x:
        #         return DriveMove.LEFT
        #     elif next_y > player_y:
        #         return DriveMove.UP
        #     elif next_y < player_y:
        #         return DriveMove.DOWN

        # return DriveMove.NONE


        # player_x, player_y = sensor_data[SensorData.PLAYER_LOCATION]
        # player_pos = (player_x, player_y)

        # # Get the pod ID we are currently carrying (if any)
        # self.carrying_pod_id = next(
        #     (pair[1] for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS] if pair[0] == self.drive_id), 
        #     None
        # )

        # carrying_pod = self.carrying_pod_id is not None

        # if carrying_pod:
        #     # If carrying a pod, check if we've reached a goal and drop it off
        #     goals = sensor_data[SensorData.GOAL_LOCATIONS]
        #     path = self.find_shortest_path(player_pos, goals, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         # Drop the pod and add it to the collected pods set
        #         self.collected_pods.add(self.carrying_pod_id)
        #         self.carrying_pod_id = None  # Reset carrying pod ID
        #         return DriveMove.DROP_POD
        # else:
        #     # If not carrying a pod, find the next available pod that hasn't been collected
        #     pods = [pod for pod in sensor_data[SensorData.REAL_TIME_POD_LOCATIONS] 
        #             if pod[0] not in self.collected_pods]  # Filter out collected pods
            
        #     if not pods:
        #         return DriveMove.NONE  # No more pods to collect

        #     # Find the shortest path to one of the uncollected pods
        #     path = self.find_shortest_path(player_pos, pods, sensor_data)

        #     if not path:
        #         return DriveMove.NONE

        #     if len(path) == 1 and path[0] == player_pos:
        #         # Pick up the pod
        #         self.carrying_pod_id = sensor_data[SensorData.REAL_TIME_POD_LOCATIONS][pods.index(path[0])][0]
        #         return DriveMove.LIFT_POD

        # # If there are still steps left in the path, move towards the next tile
        # if len(path) > 1:
        #     next_x, next_y = path[1] 
        #     if next_x > player_x:
        #         return DriveMove.RIGHT
        #     elif next_x < player_x:
        #         return DriveMove.LEFT
        #     elif next_y > player_y:
        #         return DriveMove.UP
        #     elif next_y < player_y:
        #         return DriveMove.DOWN

        # return DriveMove.NONE

        player_x, player_y = sensor_data[SensorData.PLAYER_LOCATION]
        player_pos = (player_x, player_y)

        # Get the pod ID we are currently carrying (if any)
        self.carrying_pod_id = next(
            (pair[1] for pair in sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS] if pair[0] == self.drive_id), 
            None
        )

        carrying_pod = self.carrying_pod_id is not None

        if carrying_pod:
            # If carrying a pod, check if we've reached a goal and drop it off
            goals = sensor_data[SensorData.GOAL_LOCATIONS]
            path = self.find_shortest_path(player_pos, goals, sensor_data)

            if not path:
                return DriveMove.NONE

            if len(path) == 1 and path[0] == player_pos:
                # Drop the pod and add it to the collected pods set
                self.collected_pods.add(self.carrying_pod_id)
                # self.carrying_pod_id = None  # Reset carrying pod ID
                print(f"Dropped off pod ID: {self.collected_pods}")

                return DriveMove.DROP_POD
        else:
            # If not carrying a pod, find the next available pod that hasn't been collected
            pods = []

            for pod in sensor_data[SensorData.REAL_TIME_POD_LOCATIONS]:
                if pod not in self.collected_pods:
                    pods.append(pod)
            

            # pods = [pod for pod in sensor_data[SensorData.REAL_TIME_POD_LOCATIONS] 
            #         if pod[0] not in self.collected_pods]  # Filter out collected pods
            
            if not pods:
                return DriveMove.NONE  # No more pods to collect

            # Find the shortest path to one of the uncollected pods
            path = self.find_shortest_path(player_pos, pods, sensor_data)

            if not path:
                return DriveMove.NONE

            if len(path) == 1 and path[0] == player_pos:
                # Pick up the pod
                # self.carrying_pod_id = sensor_data[SensorData.REAL_TIME_POD_LOCATIONS][pods.index(path[0])][0]
                # print(f"Picked up pod ID: {self.carrying_pod_id}")
                # return DriveMove.LIFT_POD

                pod_to_pick_up = None
                for pod in pods:
                    if pod[1] == path[0]:  # pod[1] contains the coordinates, path[0] is the target position
                        pod_to_pick_up = pod
                        break
                if pod_to_pick_up:
                    self.carrying_pod_id = pod_to_pick_up[0]  # pod[0] contains the pod ID
                    print(f"Picked up pod ID: {self.carrying_pod_id}")
                    return DriveMove.LIFT_POD

        # If there are still steps left in the path, move towards the next tile
        if len(path) > 1:
            next_x, next_y = path[1] 
            if next_x > player_x:
                return DriveMove.RIGHT
            elif next_x < player_x:
                return DriveMove.LEFT
            elif next_y > player_y:
                return DriveMove.UP
            elif next_y < player_y:
                return DriveMove.DOWN

        return DriveMove.NONE



            


            