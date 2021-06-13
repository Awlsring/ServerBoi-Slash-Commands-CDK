#!/bin/bash
tsc

pip install lambdas/handlers/interactions/
pip install lambdas/handlers/provision_workflow/provision_lambda

# Package for layers
mkdir -p lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages
mkdir -p lambdas/layers/cloud_apis/python/lib/python3.8/site-packages

pip install git+https://github.com/ServerBoiTeam/ServerBoi-Python-Utils.git --upgrade -t lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages
pip install linode_api4 --upgrade -t lambdas/layers/cloud_apis/python/lib/python3.8/site-packages
cd lambdas/layers/serverboi_utils
zip -r serverboi_utils.zip .
rm -rf python
cd ../cloud_apis
zip -r cloud_apis.zip .
rm -rf python
