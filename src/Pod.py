from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Pod:
    pod_id: int
    original_position: Optional[Tuple[int, int]] = None
    target_goal: Optional[Tuple[int, int]] = None
    contents = []