#!/bin/bash

#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100-40g
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=4000
####### -o ./runs/%j-slurm-run.txt # STDOUT/STDERR
####### --nodelist=falcon5

module load any/python/3.8.3-conda

source ~/miniconda3/etc/profile.d/conda.sh
conda activate e2e

# --model-type pilotnet-control, pilotnet-conditional; only pilotnet-conditional supports turns (conditions)
# --batch-sampler old, weighted, turn-weighted
# --loss mae, mse, huber; weighted losses use waypoints for their computation
# --aug-color-prob
# --aug-noise-prob
# --aug-blur-prob
/gpfs/space/home/zaliznyi/miniconda3/envs/e2e/bin/python train.py \
    --input-modality nvidia-camera \
    --output-modality steering_angle \
    --camera-name front_wide \
    --dataset-folder /gpfs/space/projects/rally2023/rally-estonia-cropped-antialias \
    --wandb-project testing \
    --model-name swin-conditional-steering-angle \
    --model-type swin-conditional \
    --max-epochs 100 \
    --patience 100 \
    --batch-size 512 \
    --learning-rate 0.0005 \
    --learning-rate-patience 5 \
    --weight-decay 0.01 \
    --batch-sampler old \
    --loss mae
