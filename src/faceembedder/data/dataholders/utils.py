from typing import List


def read_file(path: str) -> List[List[str]]:
	with open(path, "r") as file_stream:
		lines = map(lambda x: x.strip().split(), file_stream.readlines())
	return list(lines)
