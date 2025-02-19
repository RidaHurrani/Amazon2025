import random
from src.DriveInterface import DriveInterface
from src.DriveState import DriveState
from src.GameConfig import POD_PICKUP_PROBABILITY, POD_DROP_PROBABILITY
from src.Constants import DriveMove


class AIDrive(DriveInterface):
    def __init__(self, game_id):
        self.id = game_id

    def get_next_move(self, sensor_data):
        # move
        move = random.randint(1,4)
        return DriveMove(move)
        