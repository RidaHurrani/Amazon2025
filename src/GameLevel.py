from dataclasses import dataclass


@dataclass
class GameLevel:
    name: str
    num_ai_drives: int
    num_pods: int  # All pods must be collected
    sensor_range: int