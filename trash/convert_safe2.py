from src.faceembedder.data.datasets import  ms1mv2

converter = ms1mv2.MS1MV2InsightFaceConverter(src_path="/datasets/raw/MS1MV2-InsightFace",
                                                  dst_path="/datasets/interim/folder/MS1MV2-InsightFace",
                                                  writer="FolderWriter", verbose=True)

converter.execute()