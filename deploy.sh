#!/bin/bash

set -e
echo "INSTALLING VIRTUALENV"
pip3.11 install virtualenv

echo "CREATING VIRTUALENV"
virtualenv venv
./venv/bin/pip install -r requirements.txt

echo "RUNNING UNIT TESTS"
export PYTHONPATH="${PYTHONPATH}:`pwd`"
./venv/bin/python -m unittest discover -s tests/unittests

echo "CREATING CHALICE PACKAGE"
./venv/bin/chalice package --merge-template resources.json out 

echo "CREATING CLOUD FORMATION PACKAGE"
awscliv2 cloudformation package --template-file out/sam.json --output-template-file out/packaged-template.yaml --s3-bucket yess-app 

echo "DEPLOYING CLOUD FORMATION PACKAGE"
awscliv2 cloudformation deploy --template-file out/packaged-template.yaml --stack-name yess-app --capabilities CAPABILITY_NAMED_IAM

echo "RUNNING E2E TESTS"
./venv/bin/pytest tests/e2e