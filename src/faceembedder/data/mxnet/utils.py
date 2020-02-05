import os.path as osp

from .recardio import MXIndexedRecordIO


def load_records(path: str, idx_filename: str = "train.idx", rec_filename: str = "train.rec") -> MXIndexedRecordIO:
	index_path = osp.join(path, idx_filename)
	records_path = osp.join(path, rec_filename)
	indexed_records = MXIndexedRecordIO(index_path, records_path, flag="r")
	return indexed_records
