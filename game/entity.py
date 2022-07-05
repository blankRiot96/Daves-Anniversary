import enum

class EntityStates(enum.Enum):
	WALK = enum.auto()
	IDLE = enum.auto()
	JUMP = enum.auto()