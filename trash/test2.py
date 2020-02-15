import os
from tqdm import tqdm

import cv2
import matplotlib.pyplot as plt

from src.faceembedder.data.enums import Phase
from src.faceembedder.data.records import ClassificationRecord
from src.faceembedder.data.mxnet import MXIndexedRecordIO, unpack, unpack_img
from src.faceembedder.data.writers import FolderWriter, BcolzWriter
from src.faceembedder.data.readers import FolderReader, BcolzReader


def check_writer():
	path = "/project/data/faces_umd"
	index_path = os.path.join(path, "train.idx")
	records_path = os.path.join(path, "train.rec")
	indexed_records = MXIndexedRecordIO(index_path, records_path, flag="r")
	header, _ = unpack(indexed_records.read_idx(0))
	max_index = int(header.label[0])

	# writer = BcolzWriter("/project/data/zz_umdfaces")
	writer = FolderWriter("/project/data/zz_umdfaces_1")

	for index in tqdm(range(1, max_index)):
		record: bytes = indexed_records.read_idx(index)
		header, image = unpack_img(record)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		label = int(header.label)

		record = ClassificationRecord(image, label, additional=(12, 123, 21))
		writer.put(record)

	writer.flush()

# def test():
	# writer = FolderWriter("/project/data/zz_umdfaces_folder")
	# converter = umdfaces.InsightFaceConverter(writer, verbose=True)
	# # converter.execute_from("/project/data/faces_umd")
	# reader = FolderReader("/project/data/zz_umdfaces_folder")
	# dataset = umdfaces.UMDFacesDataHolder(reader)

	# writer = BcolzWriter("/project/data/zz_umdfaces_bcolz")
	# converter = umdfaces.InsightFaceConverter(writer, verbose=True)
	# converter.execute_from("/project/data/faces_umd")
	# reader = BcolzReader("/project/data/zz_umdfaces_bcolz")
	# dataset = umdfaces.UMDFacesDataHolder(reader)

def lfw():
	from src.faceembedder.data.datasets import lfw
	# writer = FolderWriter("/datasets/interim/folder/LFW-Origin")
	# converter = lfw.OriginConverter(writer, verbose=True)
	# converter.execute_from("/datasets/raw/LFW-Origin")
	# from src.faceembedder.data.datasets import lfw
	reader_ins = FolderReader("/datasets/interim/folder/LFW-InsightFace")
	dataholder_ins = lfw.LFWOriginDataHolder(reader_ins, check_properties=False)

	reader_or = FolderReader("/datasets/interim/folder/LFW-Origin")
	dataholder_or = lfw.LFWOriginDataHolder(reader_or, check_properties=True)

	pair = dataholder_or.pairs[0]
	print(pair.label)
	plt.imshow(dataholder_or[pair.idx_1].image)
	plt.show()
	plt.figure()
	plt.imshow(dataholder_or[pair.idx_2].image)
	plt.show()


def main():
	# check_writer()
	# test(

	from src.faceembedder.data import CONVERTERS_REGISTRY, DATAHOLDERS_REGISTRY

	# converter = CONVERTERS_REGISTRY.get("LFW", "Origin")(
	# 	"/datasets/raw/LFW-Origin",
	# 	"/datasets/interim/folder/test",
	# 	"FolderWriter",
	# 	verbose=True
	# )
	# converter.execute()

	# data_holder = DATAHOLDERS_REGISTRY.get("LFWDataHolder")(
	# 	"/datasets/interim/folder/test",
	# 	"FolderReader",
	# 	check_properties=True
	# )

	from src.faceembedder.data.datasets.vggface2 import VGGFace2InsightFaceDataHolder
	data_holder = VGGFace2InsightFaceDataHolder("/datasets/interim/folder/VGGFace2-InsightFace", reader="FolderReader", check_properties=False)
	z = data_holder[3]

	a = 4


if __name__ == "__main__":
	main()