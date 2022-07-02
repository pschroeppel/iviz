#!/bin/bash 

export IVIZ_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PYTHONPATH="$IVIZ_PATH/python:$PYTHONPATH"
export PATH="$IVIZ_PATH/bin:$PATH"

