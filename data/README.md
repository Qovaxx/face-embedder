# Data

## Datasets naming convention
...

## Project datasets formats
...

## Adding your datasets
...

Datasets below may not be fully completed, as the authors intended. The data structure is specifically designed for this
project, so some of the original file may not be available.

## Train Datasets

* #### MS1MV2
    This dataset is also known as MS1M-Arcface and it is one of the cleanup versions of the original dataset
    MS1M (MS-Celeb-1M).
    * **[MS1MV2-InsightFace](https://github.com/deepinsight/insightface/wiki/Dataset-Zoo)
        (85.742 ids, 5.822.653 images)**
        
        Desc WIP
         * Folder structure:
            ```
                raw/
                ├── MS1MV2-InsightFace/
                │   ├── train.idx
                │   ├── train.rec
                └── ...
            ```
         * Download links:
            * [train.idx](https://www.dropbox.com/s/wpx6tqjf0y5mf6r/faces_ms1m-refine-v2_112x112.zip?dl=0)
            * [train.rec](https://www.dropbox.com/s/wpx6tqjf0y5mf6r/faces_ms1m-refine-v2_112x112.zip?dl=0)
        

* #### VGGFace2
    The dataset has an intersection of [53](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/meta/class_overlap_vgg1_2.txt)
    ids with the previous version VGGFace
    * **[VGGFace2-Origin](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/)
        (9131 ids, 3.311.286 images)**
        
        Dataset from the `original site` (preliminary application required). For each image, there are gender,
        facial landmarks, and bbox coordinates. For 30k ids, the following attributes are available: the presence of
        a mustache and beard, hat, glasses (the intersection is less than 30k). The data is splitted into train and test.
         * Folder structure:
            ```
                raw/
                ├── VGGFace2-Origin/
                │   ├── bb_landmark/
                |   |   ├── loose_bb_test.csv
                |   |   ├── loose_bb_train.csv
                |   |   ├── loose_landmark_test.csv
                |   |   ├── loose_landmark_train.csv
                |   |   └── ...
                │   ├── train/
                |   |   ├── n000002/
                |   |   ├── n000003/
                |   |   └── ...
                │   ├── test/
                |   |   ├── n000001/
                |   |   ├── n000009/
                |   |   └── ...
                │   ├── 07-Mustache_or_Beard.txt
                │   ├── 08-Wearing_Hat.txt
                │   ├── 09-Eyeglasses.txt
                │   ├── 10-Sunglasses.txt
                │   ├── identity_meta.csv
                │   ├── test_list.txt
                │   ├── train_list.txt
                └── ...
            ```
         * Download links:
            * [bb_landmark](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/meta/bb_landmark.tar.gz)
            * [train](http://zeus.robots.ox.ac.uk/vgg_face2/get_file?fname=vggface2_train.tar.gz)
            * [test](http://zeus.robots.ox.ac.uk/vgg_face2/get_file?fname=vggface2_test.tar.gz)
            * [07-Mustache_or_Beard.txt](https://raw.githubusercontent.com/ox-vgg/vgg_face2/master/attributes/07-Mustache_or_Beard.txt)
            * [08-Wearing_Hat.txt](https://raw.githubusercontent.com/ox-vgg/vgg_face2/master/attributes/08-Wearing_Hat.txt)
            * [09-Eyeglasses.txt](https://raw.githubusercontent.com/ox-vgg/vgg_face2/master/attributes/09-Eyeglasses.txt)
            * [10-Sunglasses.txt](https://raw.githubusercontent.com/ox-vgg/vgg_face2/master/attributes/10-Sunglasses.txt)
            * [identity_meta.csv](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/meta/identity_meta.csv) - correct the comma in line 652
            * [test_list.txt](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/meta/test_list.txt)
            * [train_list.txt](http://www.robots.ox.ac.uk/~vgg/data/vgg_face2/meta/train_list.txt)

    * **[VGGFace2-InsightFace](https://github.com/deepinsight/insightface/wiki/Dataset-Zoo)
        (8.631 ids, 3.137.807 images)**
        
        Dataset from the `InsightFaceDatasetZoo`. The data contains only 8.631 training identities from the original
        dataset, 500 test identities and their photos are not included. Also, preprocessing for face alignment has
        already been applied to images and resolution has been changed to 112x112
         * Folder structure:
            ```
                raw/
                ├── VGGFace2-InsightFace/
                │   ├── train.idx
                │   ├── train.rec
                └── ...
            ```
         * Download links:
            * [train.idx](https://www.dropbox.com/s/m9pm1it7vsw3gj0/faces_vgg2_112x112.zip?dl=0)
            * [train.rec](https://www.dropbox.com/s/m9pm1it7vsw3gj0/faces_vgg2_112x112.zip?dl=0)



## Validation Datasets
Validation datasets *for the verification task* should include annotation for image pairs

* #### LFW
    * **[LFW-Origin](http://vis-www.cs.umass.edu/lfw/#funnel_cite) 
        (5.749 ids | 13.233 images | 6.000 pairs)** 
        
        Dataset from the `original site`, designed for the verification task. No train/val/test split and no folds
         * Folder structure:
            ```
                raw/
                ├── LFW-Origin/
                │   ├── lfw/
                |   |   ├── AJ_Cook/
                |   |   ├── AJ_Lamas/
                |   |   └── ...
                │   ├── lfw-funneled/
                |   |   ├── AJ_Cook/
                |   |   ├── AJ_Lamas/
                |   |   └── ...
                │   ├── lfw-deepfunneled/
                |   |   ├── AJ_Cook/
                |   |   ├── AJ_Lamas/
                |   |   └── ...
                │   ├── pairs.txt
                └── ...
            ```
         * Download links:
            * [lfw](http://vis-www.cs.umass.edu/lfw/lfw.tgz)
            * [lfw-funneled](http://vis-www.cs.umass.edu/lfw/lfw-funneled.tgz)
            * [lfw-deepfunneled](http://vis-www.cs.umass.edu/lfw/lfw-deepfunneled.tgz)
            * [pairs.txt](http://vis-www.cs.umass.edu/lfw/pairs.txt)

    * **[LFW-InsightFace](https://github.com/deepinsight/insightface/wiki/Dataset-Zoo#face-recognition-validation-datasets) 
        (4.281 ids | 12.000 images | 6.000 pairs)**

        Dataset from the `InsightFaceDatasetZoo` contains only part of the data of the original dataset 
        (only images for pairs are available). Also, preprocessing for face alignment has already been applied to images
        and resolution has been changed to 112x112. No train/val/test split and no folds 
         
         *It isn't known what format of the original dataset is taken as a basis [original, funneled, deepfunneled]*
         * Folder structure:
            ```
                raw/
                ├── LFW-InsightFace/
                │   ├── lfw.bin
                │   ├── pairs.txt
                └── ...
            ```
         * Download links:
            * [lfw.bin](https://www.dropbox.com/s/fv0y30mawsejweu/faces_umd.zip?dl=0)
            * [pairs.txt](http://vis-www.cs.umass.edu/lfw/pairs.txt)