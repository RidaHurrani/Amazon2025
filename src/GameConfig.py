from src.GameLevel import GameLevel


WINDOW_DIMENSIONS = [1200,800]
GRID_BLOCK_DIMENSIONS = [40, 40]
SCORE_BANNER_HEIGHT = 40

FPS_LIMIT = 5

END_SCREEN_WAIT_TIME_SEC = 3

GAME_LEVELS = [
    GameLevel(name='Level 1 - Collect One Pods',
             num_ai_drives=0,
             num_pods=1,
             sensor_range=-1),
    GameLevel(name='Level 2 - Collect One Pods with AI Drives',
             num_ai_drives=2,
             num_pods=1,  # 5 pods with AI drives
             sensor_range=-1),
    GameLevel(name='Level 3 - Collect 2 Pods with AI Drives',
             num_ai_drives=5,
             num_pods=2,
             sensor_range=-1),
    GameLevel(name='Level 4 - Collect 5 Pods with Minimum Move ',
              num_ai_drives=0,
              num_pods=5,
              sensor_range=-1)
]

MAX_MOVES_PER_ROUND = 1000

POD_PICKUP_PROBABILITY = 0.8
POD_DROP_PROBABILITY = 0.1

MIN_GOAL_DIST = 10

class DynamicConfig:
    def __init__(self):
        self.num_pods = 10
        self.energy_limit = 100
        self.pod_values = [10, 20, 30]
        
    def adjust_difficulty(self, player_score: int):
        """Adjust game parameters based on player performance"""
        if player_score > 1000:
            self.num_pods += 5
            self.energy_limit -= 10
        elif player_score < 500:
            self.num_pods -= 2
            self.energy_limit += 10
