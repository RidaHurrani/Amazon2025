from enum import Enum


class DriveMove(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    LIFT_POD = 5
    DROP_POD = 6

class Heading(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class SensorData(Enum):
    FIELD_BOUNDARIES = 'field_boundaries'
    DRIVE_LOCATIONS = 'drive_locations'
    REAL_TIME_POD_LOCATIONS = 'pod_locations'
    PLAYER_LOCATION = 'player_location'
    GOAL_LOCATIONS = 'goal_locations'
    DRIVE_LIFTED_POD_PAIRS = 'drive_lifted_pod_pairs'
    POD_TARGET_GOALS = 'pod_target_goals'  # New field for pod-goal assignments


MOVE_TO_HEADING_MAP = {
    DriveMove.NONE: -1,
    DriveMove.UP: Heading.NORTH,
    DriveMove.DOWN: Heading.SOUTH,
    DriveMove.RIGHT: Heading.EAST,
    DriveMove.LEFT: Heading.WEST
}
