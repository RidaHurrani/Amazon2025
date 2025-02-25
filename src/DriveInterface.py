from abc import ABC, abstractmethod
from src.Constants import DriveMove


class DriveInterface(ABC):
    def __init__(self, game_id):
        self.id = game_id

    @abstractmethod
    def get_next_move(self, sensor_data) -> DriveMove:
        pass

