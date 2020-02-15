from typing import NoReturn
from typing import List
from tqdm import tqdm

import cv2

from ..mxnet import (
	load_records,
	unpack_img
)
from ..records import ClassificationRecord


def read_file(path: str) -> List[List[str]]:
	with open(path, "r") as file_stream:
		lines = map(lambda x: x.strip().split(), file_stream.readlines())
	return list(lines)

def execute_insightface(self) -> NoReturn:
	indexed_records = load_records(self._src_path)
	iter = range(1, indexed_records.get_max_index())
	if self._verbose:
		iter = tqdm(iter, total=len(iter), desc="Converted: ")

	for index in iter:
		record = indexed_records.read_idx(index)
		header, image = unpack_img(record)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		label = int(header.label)
		record = ClassificationRecord(image, label)
		self._writer.put(record)
	self._writer.flush()
