#!/bin/bash
tsc

pip install lambdas/handlers/interactions/
pip install lambdas/handlers/provision_workflow/provision_lambda

# Package for layers
mkdir -p lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages
#mkdir -p lambdas/layers/aws_enums/python/lib/python3.8/site-packages
#mkdir -p lambdas/layers/linode_enums/python/lib/python3.8/site-packages

pip install git+https://github.com/ServerBoiTeam/ServerBoi-Python-Utils.git -t lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages
#pip install git+https://github.com/Awlsring/AWS-Enums-Python.git -t lambdas/layers/aws_enums/python/lib/python3.8/site-packages
#pip install git+https://github.com/Awlsring/Linode-Enums-Python.git -t lambdas/layers/linode_enums/python/lib/python3.8/site-packages

#zip -r lambdas/layers/aws_enums/aws_enums.zip lambdas/layers/aws_enums/python
#zip -r lambdas/layers/linode_enums/linode_enums.zip lambdas/layers/linode_enums/python
zip -r lambdas/layers/serverboi_utils/serverboi_utils.zip lambdas/layers/serverboi_utils/python

#rm -rf lambdas/layers/aws_enums/python
#rm -rf lambdas/layers/linode_enums/python
rm -rf lambdas/layers/serverboi_utils/python