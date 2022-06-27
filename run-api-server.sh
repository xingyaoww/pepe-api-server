#!/bin/bash

NUM_WORKERS=2
CUDA_DEVICE="0"
WORK_DIR=`pwd`
API_PORT=6667

export DATA_DIR=$WORK_DIR/data;
export PYTHONPATH=$WORK_DIR;
export CUDA_VISIBLE_DEVICES=$CUDA_DEVICE;

gunicorn -w $NUM_WORKERS -b 0.0.0.0:$API_PORT --timeout 600 app:app

# For debugging purpose
# python3 -u app.py

