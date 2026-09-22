from .fcfs import schedule_fcfs
from .priority import schedule_priority
from .round_robin import schedule_round_robin
from .sjf import schedule_sjf
from .srtf import schedule_srtf

__all__ = ["schedule_fcfs", "schedule_sjf", "schedule_srtf", "schedule_round_robin", "schedule_priority"]
