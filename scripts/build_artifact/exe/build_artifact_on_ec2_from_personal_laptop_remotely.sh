#!/bin/bash
# Run this from your local laptop.
# Pre-reqs:
#  -setup build environment on an amazonlinux2 EC2 instance using the
#    "ec2_instance_one-time-setup.sh" script in the "first_time_run" dir.
#
# This script will...:
#  -SSH into the EC2 instance.
#  -create a python 3.7.7 virtualenv.
#  -clone the repo.
#  -pull & fetch all branches
#  -jump to the branch specified in the "BRANCH_TO_BUILD" env var on line 28 of this file.
#  -build the .zip to be uploaded to Lambda.
#  -terminate the SSH session.
#  -scp the .zip from EC2 to local laptop (trustar-aws-guard-duty/build/function.zip)
#  -SSH into the EC2 instance again.
#  -delete the temp directory that contains the repo cloneed from Git.
#  -delete the python 3.7.7 virtualenv.



rm -rf ../build/  # in case it's already there.
ssh gdbuilder << EOF
BRANCH_TO_BUILD=master
sudo yum update -y
pip install --upgrade pip setuptools
rm -rf temp_build
mkdir temp_build
cd temp_build
git clone git@github.com:trustar/trustar-aws-guard-duty.git
cd trustar-aws-guard-duty
git fetch --all
git pull --all
git checkout $BRANCH_TO_BUILD
mkdir ./build
cp -R ./src/exe/* ./build/
pipenv lock -r > requirements.txt
pipenv run pip install -r ./requirements.txt --target ./build/
cd build
zip -r9 ../function.zip .
EOF
mkdir ../build
scp gdbuilder:temp_build/trustar-aws-guard-duty/function.zip ../build/
ssh gdbuilder << EOF
rm -rf temp_build
pyenv virtualenv-delete -f gdbuild-3.7.7
EOF
