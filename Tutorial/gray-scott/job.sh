#!/bin/bash
#SBATCH -A CSC143
#SBATCH -J gs4
#SBATCH -N 32
#SBATCH -t 02:00:00
#SBATCH -o gs4.o
#SBATCH -e gs4.e
#SBATCH \-\-mem=0

# andes
module load cmake/3.18.4
module load gcc/9.3.0
module load cuda/10.2.89
module load openmpi/4.0.4
module load python/3.7-anaconda3

echo "======================"
date

#time srun -N 32 --ntasks-per-node 32 build/gray-scott simulation/settings-files-gs1.json 
#time srun -N 32 --ntasks-per-node 32 build/gray-scott simulation/settings-files-gs2.json 
#time srun -N 32 --ntasks-per-node 32 build/gray-scott simulation/settings-files-gs3.json 
time srun -N 32 --ntasks-per-node 32 build/gray-scott simulation/settings-files-gs4.json 

