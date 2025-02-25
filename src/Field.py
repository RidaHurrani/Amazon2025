import random
from src.Constants import DriveMove, SensorData, MOVE_TO_HEADING_MAP
from src.DriveState import DriveState
from src.GameConfig import POD_PICKUP_PROBABILITY, MIN_GOAL_DIST
from src.GameTile import GameTile
from src.Utils import manhattan_dist_2D
from src.GameIdProvider import GameIdProvider
from src.Pod import Pod


SENSOR_DATA_FILTER_FIELDS = [
    SensorData.FIELD_BOUNDARIES,
    SensorData.DRIVE_LOCATIONS,
    SensorData.REAL_TIME_POD_LOCATIONS,
    SensorData.DRIVE_LIFTED_POD_PAIRS,
    SensorData.POD_TARGET_GOALS
]

class Field:
    def __init__(self, field_grid_width, field_grid_height):
        # Initialize backing grid
        self.field_grid = [[GameTile(drive=None, pod=None, is_goal=False) for row in range(field_grid_height)] for col in range(field_grid_width)]
        self.drive_pod_pairings_map = {} # key = drive object ID, val = Pod currently lifted by drive
        self.drive_states_map = {} # key = drive object ID, val = DriveState object for drive
        self.pod_locations_map = {} # key = pod object ID, val = [x, y] coords of pod
        self.drive_to_game_id_map = {} # key = drive object ID, val = assigned game id
        self.player_id = ''
        self.field_boundary_coords = self.build_list_of_field_boundaries()
        self.sensor_range = -1
        self.pods = []
        self.goal_coords_list = []
        self.collected_pods = set()  # Set of collected pod IDs
        
        # Add ID providers
        self.pod_id_provider = GameIdProvider()

    def set_sensor_range(self, sensor_range):
        self.sensor_range = sensor_range

    def spawn_goal(self, num_goals):
        """Spawn one goal for each pod we'll create"""
        for _ in range(num_goals):
            x = random.randint(0, len(self.field_grid) - 1)
            y = random.randint(0, len(self.field_grid[0]) - 1)
            while any(manhattan_dist_2D([x, y], goal) < MIN_GOAL_DIST for goal in self.goal_coords_list):
                x = random.randint(0, len(self.field_grid) - 1)
                y = random.randint(0, len(self.field_grid[0]) - 1)
            self.field_grid[x][y].is_goal = True
            self.goal_coords_list.append([x, y])

    def spawn_player(self, player, player_id):
        if not self.goal_coords_list:
            raise Exception('No goals exist, cannot decide spawn location for player. Call Field.spawn_goal before Field.spawn_player')
        field_x = len(self.field_grid) - 1
        field_y = len(self.field_grid[0]) - 1
        x = random.randint(field_x // 4, 3 * field_x // 4)
        y = random.randint(field_y // 4, 3 * field_y // 4)
        while any(manhattan_dist_2D([x, y], goal_coords) < MIN_GOAL_DIST for goal_coords in self.goal_coords_list):
            y = random.randint(0, len(self.field_grid[0]) - 1)
            x = random.randint(0, len(self.field_grid) - 1)
        self.field_grid[x][y].drive = player
        self.drive_states_map[str(player)] = DriveState(x=x, y=y)
        self.player_id = str(player)
        self.drive_to_game_id_map[str(player)] = player_id

    def spawn_new_ai_drive(self, ai_drive):
        x = random.randint(0, len(self.field_grid) - 1)
        y = random.randint(0, len(self.field_grid[0]) - 1)
        while self.field_grid[x][y].drive != None: 
            y = random.randint(0, len(self.field_grid[0])-1)
            x = random.randint(0, len(self.field_grid)-1)
        self.field_grid[x][y].drive = ai_drive
        self.drive_states_map[str(ai_drive)] = DriveState(x=x, y=y)
        self.drive_to_game_id_map[str(ai_drive)] = ai_drive.id

    def spawn_target_pod(self, pod, can_other_drives_lift=False):
        field_x = len(self.field_grid) - 1
        field_y = len(self.field_grid[0]) - 1
        x = random.randint(field_x // 4, 3 * field_x // 4)
        y = random.randint(field_y // 4, 3 * field_y // 4)
        while any(manhattan_dist_2D([x, y], goal_coords) < MIN_GOAL_DIST for goal_coords in self.goal_coords_list):
            y = random.randint(0, len(self.field_grid[0])-1)
            x = random.randint(0, len(self.field_grid)-1)

        self.field_grid[x][y].pod = pod
        self.pod_locations_map[str(pod)] = [x, y]

        if can_other_drives_lift == True:
            if self.field_grid[x][y].drive != None:
                if random.uniform(0, 1) < POD_PICKUP_PROBABILITY: # start with pod on drive
                    self.drive_pod_pairings_map[str(self.field_grid[x][y].drive)] = pod

    def spawn_new_pod(self, pod_id: int):
        """Spawn a new pod and assign it a unique target goal"""
        # Find spawn location
        x = random.randint(0, len(self.field_grid) - 1)
        y = random.randint(0, len(self.field_grid[0]) - 1)
        while self.field_grid[x][y].pod != None or self.field_grid[x][y].drive != None:
            x = random.randint(0, len(self.field_grid) - 1)
            y = random.randint(0, len(self.field_grid[0]) - 1)
        original_position = (x, y)
        pod = Pod(pod_id, original_position)
        # Assign a unique target goal to this pod
        available_goals = [goal for goal in self.goal_coords_list 
                          if not any(self.field_grid[i][j].pod and 
                                   self.field_grid[i][j].pod.target_goal == tuple(goal)
                                   for i in range(len(self.field_grid))
                                   for j in range(len(self.field_grid[0])))]

        if available_goals:
            pod.target_goal = tuple(random.choice(available_goals))
            print(f"Pod {pod.pod_id} assigned to goal {pod.target_goal}")

        self.pods.append(pod)
        self.field_grid[x][y].pod = pod
        self.pod_locations_map[str(pod)] = [x, y]

        if self.field_grid[x][y].drive != None and str(self.field_grid[x][y].drive) != self.player_id:
            if random.uniform(0, 1) < POD_PICKUP_PROBABILITY:
                self.drive_pod_pairings_map[str(self.field_grid[x][y].drive)] = pod

    def is_drive_player(self, drive):
        return str(drive) == self.player_id

    def process_move_for_drive(self, move, drive):
        # Debug log:
        # print("Received move:", move)
        current_drive_state = self.drive_states_map[str(drive)]

        if self.will_next_move_crash(move, drive):
            if self.is_drive_player(drive):
                self.field_grid[current_drive_state.x][current_drive_state.y].drive = None
                self.field_grid[current_drive_state.x][current_drive_state.y].is_crash = True
                return False
            else:
                # Do not move AI drives into invalid states. Skip turn for AI instead
                return True
        else:
            # Process Pod operations before moves
            if move == DriveMove.LIFT_POD:
                if self.field_grid[current_drive_state.x][current_drive_state.y].pod != None:
                    self.drive_pod_pairings_map[str(drive)] = self.field_grid[current_drive_state.x][current_drive_state.y].pod
                    print(f"Picked up pod at {current_drive_state.x}, {current_drive_state.y}")
                else:
                    if self.is_drive_player(drive):
                        print(f'Player drive {drive} tried picking up a pod, but no pod was present at current state')
            elif move == DriveMove.DROP_POD:
                if self.is_drive_carrying_a_pod(drive):
                    pod = self.drive_pod_pairings_map[str(drive)]
                    current_pos = (current_drive_state.x, current_drive_state.y)
                    
                    # Only allow dropping at pod's target goal
                    if current_pos == pod.target_goal:
                        self.collected_pods.add(str(pod))
                        del self.drive_pod_pairings_map[str(drive)]
                        print(f"Pod {pod.pod_id} delivered to its target goal {pod.target_goal}")
                    else:
                        print(f"Can't drop pod here - not its target goal {pod.target_goal}")
                        return True  # Don't allow dropping at wrong location
                else:
                    if self.is_drive_player(drive):
                        print(f'Player drive {drive} tried dropping a pod, but wasn\'t carrying one')
            else:
                # Move drive
                self.field_grid[current_drive_state.x][current_drive_state.y].drive = None
                if self.is_drive_carrying_a_pod(drive):
                    self.field_grid[current_drive_state.x][current_drive_state.y].pod = None

                current_drive_state.update_state_from_move(move)
                self.field_grid[current_drive_state.x][current_drive_state.y].drive = drive
                self.drive_states_map[str(drive)] = current_drive_state
                if self.is_drive_carrying_a_pod(drive):
                    self.field_grid[current_drive_state.x][current_drive_state.y].pod = self.drive_pod_pairings_map[str(drive)]
                    self.pod_locations_map[str(self.field_grid[current_drive_state.x][current_drive_state.y].pod)] = [current_drive_state.x, current_drive_state.y]
                
                # Update drive heading for UI
                new_heading = MOVE_TO_HEADING_MAP[move]
                if new_heading != -1:
                    self.field_grid[current_drive_state.x][current_drive_state.y].drive_heading = new_heading

            return True

    def will_next_move_crash(self, move, drive):
        current_drive_state = self.drive_states_map[str(drive)]
        new_x, new_y = current_drive_state.get_next_state_from_move(move)

        if new_x < 0 or new_x >= len(self.field_grid) or new_y < 0 or new_y >= len(self.field_grid[0]):
            # Drive will exit the field
            return True
        elif (new_x, new_y) != current_drive_state.to_tuple():
            if self.field_grid[new_x][new_y].drive != None:
                # Drive will crash into another field
                return True
            elif self.field_grid[new_x][new_y].pod != None and self.is_drive_carrying_a_pod(drive):
                # Drive is carrying a pod and will crash into another pod
                return True
        else:
            return False

    def is_drive_carrying_a_pod(self, drive):
        return str(drive) in self.drive_pod_pairings_map.keys()

    def generate_sensor_data_for_drive(self, drive):
        """Generate sensor data dictionary for a specific drive"""
        sensor_data = {
            SensorData.FIELD_BOUNDARIES: self.field_boundary_coords,
            SensorData.DRIVE_LOCATIONS: [],
            SensorData.REAL_TIME_POD_LOCATIONS: [],
            SensorData.DRIVE_LIFTED_POD_PAIRS: self.build_drive_lifted_pod_pairs(),
            SensorData.PLAYER_LOCATION: [self.drive_states_map[self.player_id].x, self.drive_states_map[self.player_id].y],
            SensorData.GOAL_LOCATIONS: self.goal_coords_list,
            SensorData.POD_TARGET_GOALS: self.pods  # Add pod-goal mapping
        }



        # Add all drive locations except the requesting drive
        for d in self.drive_states_map.keys():
            if d != str(drive):
                sensor_data[SensorData.DRIVE_LOCATIONS].append(
                    [self.drive_states_map[d].x, self.drive_states_map[d].y]
                )

        # Add all pod locations
        for p in self.pod_locations_map.keys():
            sensor_data[SensorData.REAL_TIME_POD_LOCATIONS].append(self.pod_locations_map[p])

        if self.sensor_range > 0:
            self.filter_sensor_data_for_sensor_range(sensor_data)

        return sensor_data

    def build_drive_lifted_pod_pairs(self):
        drive_lifted_pod_pair_list = []
        for drive_str in self.drive_states_map.keys():
            if drive_str in self.drive_pod_pairings_map.keys():
                drive_lifted_pod_pair_list.append([self.drive_to_game_id_map[drive_str], self.drive_pod_pairings_map[drive_str].pod_id])

        return drive_lifted_pod_pair_list

    def get_target_pod_info(self):
        if self.pod_locations_map:
            return self.pod_locations_map[next(iter(self.pod_locations_map))]
        else:
            return []

    def filter_sensor_data_for_sensor_range(self, sensor_data):
        player_state = self.drive_states_map[self.player_id]
        player_location = [player_state.x, player_state.y]
        for data_field in SENSOR_DATA_FILTER_FIELDS:
            new_data = []
            for val in sensor_data[data_field]:
                if round(manhattan_dist_2D(player_location, val)) <= self.sensor_range:
                    new_data.append(val)
            sensor_data[data_field] = new_data

    def is_winning_condition(self):
        """Check if all pods have been delivered to their specific goals"""
        # First check if all pods have been collected
        if len(self.collected_pods) != len(self.pod_locations_map):
            return False
        
        # Then check if each pod is at its target goal
        for pod_id, pod_loc in self.pod_locations_map.items():
            # Skip if pod is being carried
            if any(str(carried_pod) == pod_id for carried_pod in self.drive_pod_pairings_map.values()):
                return False
            
            # Find the pod object
            pod = None
            for x in range(len(self.field_grid)):
                for y in range(len(self.field_grid[0])):
                    if self.field_grid[x][y].pod and str(self.field_grid[x][y].pod) == pod_id:
                        pod = self.field_grid[x][y].pod
                        break
                if pod:
                    break
                
            # Check if pod is at its target goal
            if pod and pod.target_goal:
                if tuple(pod_loc) != pod.target_goal:
                    return False
                
        return True

    def build_list_of_field_boundaries(self):
        # Add top and bottom boundaries
        bottom_boundary = []
        top_boundary = []
        for i in range(len(self.field_grid) + 2):
            bottom_boundary.append([i-1, -1])
            top_boundary.append([i-1, len(self.field_grid[0])])

        # Add left and right boundaries
        left_boundary = []
        right_boundary = []
        for i in range(len(self.field_grid[0])):
            left_boundary.append([-1, i])
            right_boundary.append([len(self.field_grid), i])

        return bottom_boundary + left_boundary + top_boundary + right_boundary
    
