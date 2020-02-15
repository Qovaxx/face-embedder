from enum import Enum


class Phase(Enum):
	TRAIN = 1
	VAL = 2
	TEST = 3


class DataFormat(Enum):
	FOLDER = 1
	BCOLZ = 2
