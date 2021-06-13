#!/bin/bash
tsc

pip install lambdas/handlers/interactions/
pip install lambdas/handlers/provision_workflow/provision_lambda

# Package for layers
mkdir -p lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages

pip install git+https://github.com/ServerBoiTeam/ServerBoi-Python-Utils.git -t lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages
cd lambdas/layers/serverboi_utils
zip -r serverboi_utils.zip .

rm -rf python