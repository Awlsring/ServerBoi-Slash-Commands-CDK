#!/bin/bash

tsc

pip install lambdas/handlers/interactions/

pip install lambdas/handlers/provision

mkdir -p lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages

pip install lambdas/layers/serverboi_utils -t lambdas/layers/serverboi_utils/python/lib/python3.8/site-packages

cd lambdas/layers/serverboi_utils/python

zip -r -j lambdas/layers/serverboi_utils/serverboi_utils.zip lambdas/layers/serverboi_utils/python