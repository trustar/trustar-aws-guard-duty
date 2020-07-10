#!/bin/bash
# Run this from your local laptop.
# Pre-reqs:
#  -create a new GitHub SSH key and install it in your user account on the EC2 instance.
#  -setup Python 3.7.7 venv on the EC2 instance using the script in "first_time_run" dir.
#  -in SSH config file on your laptop, make an entry named "gdbuilder" that will
#   SSH you into the EC2 instance to a user account that has "sudo".  (usu, ec2-user)
# It will:
#  -SSH into the EC2 instance.
#  -clone the repo.
#  -pull & fetch all.
#  -jump to the EN-422/update_dependencies branch.
#  -build the .zip
#  -terminate the SSH.
#  -scp the .zip from EC2 to local.

rm -rf ../build/  # in case it's already there.
ssh gdbuilder << EOF

pyenv install 3.7.7 -s
pyenv virtualenv-delete gdbuild-3.7.7
pyenv virtualenv 3.7.7 gdbuild-3.7.7
pyenv virtualenvs
pyenv activate gdbuild-3.7.7
pyenv version
cat .python-version
pyenv rehash
python --version
pip install --upgrade pip
pip list --format=columns

rm -rf temp_build
mkdir temp_build
cd temp_build
git clone git@github.com:trustar/trustar-aws-guard-duty.git
cd trustar-aws-guard-duty
git fetch --all
git pull --all
git checkout EN-422/update_dependencies
mkdir ./build
cp -R ./src/* ./build/
pip install -r ./requirements.txt --target ./build/
cd build
zip -r9 ../function.zip .
EOF
mkdir ../build
scp gdbuilder:temp_build/trustar-aws-guard-duty/function.zip ../build/
ssh gdbuilder << EOF
rm -rf temp_build
pyenv virtualenv-delete -f gdbuild-3.7.7
EOF
