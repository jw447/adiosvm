#!/bin/bash

# andes
module load cmake/3.18.4
module load gcc/9.3.0
module load cuda/10.2.89
module load openmpi/4.0.4
module load python/3.7-anaconda3


mkdir -p  build
cd build

mkdir -p install

cmake -DCMAKE_PREFIX_PATH=/gpfs/alpine/proj-shared/csc143/jwang/io_modeling/adiosvm/Tutorial/gray-scott/build/install -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
make


