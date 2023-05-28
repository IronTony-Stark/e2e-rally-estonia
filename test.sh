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

/gpfs/space/home/zaliznyi/miniconda3/envs/e2e/bin/python test.py
