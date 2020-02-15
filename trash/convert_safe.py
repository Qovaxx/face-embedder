from src.faceembedder.data.readers import FolderReader
from src.faceembedder.data.datasets import lfw, vggface2

converter = vggface2.VGGFace2OriginConverter(src_path="/datasets/raw/VGGFace2-Origin",
                                                  dst_path="/datasets/interim/folder/VGGFace2-Origin",
                                                  writer="FolderWriter", verbose=True)
converter.execute()
