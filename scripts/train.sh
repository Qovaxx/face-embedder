#!/usr/bin/env bash
# Script to start PyTorch training in one of two modes to choose from:
# DataParallel and DistributedDataParallel, - based on the configuration file

# Example usege:
# ./train.sh \
#   --config-path=/project/configs/config.py \
#   --cuda-visible-devices=0,1,2 \
#   --is-distributed=true


IFS=","

# Args parsing
for i in "$@"; do
    case "$1" in
        -cp=*|--config-path=*)
            CONFIG_PATH="${i#*=}"
            shift
        ;;
        -cvd=*|--cuda-visible-devices=*)
            CUDA_VISIBLE_DEVICES="${i#*=}"
            shift
        ;;
        -id=*|--is-distributed=*)
            IS_DISTRIBUTED="${i#*=}"
            shift
        ;;
        *)
            echo "Invalid option $i"
            exit 1
    esac
done

read -ra GPUS <<<"$CUDA_VISIBLE_DEVICES"
GPU_COUNT="${#GPUS[@]}"


if [ $IS_DISTRIBUTED = true ]; then
    OMP_NUM_THREADS=1 \
    CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    python -m torch.distributed.launch \
        --nnodes=1 \
        --node_rank=0 \
        --nproc_per_node=$GPU_COUNT \
        $PROJECT_DIRPATH/src/faceembedder/train.py \
            --config_path=$CONFIG_PATH \
            --is_distributed

elif [ $IS_DISTRIBUTED = false ]; then
    CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    python $PROJECT_DIRPATH/src/faceembedder/train.py --config_path=$CONFIG_PATH

else
    echo "Invalid option: --is-distributed=$IS_DISTRIBUTED"
    exit 1
fi
