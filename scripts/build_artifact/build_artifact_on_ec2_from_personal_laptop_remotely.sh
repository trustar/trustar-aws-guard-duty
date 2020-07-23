#!/bin/bash
# Run this from your local laptop, current working directory should be
#  "trustar-aws-guard-duty/scripts/build_artifact/" when executed.
#
# Pre-reqs:
#  -setup build environment on an amazonlinux2 EC2 instance using the
#    "ec2_instance_one-time-setup.sh" script in the "first_time_run" dir.
#
# This script will...:
#  -SSH into the EC2 instance.
#  -make temp directory that can be easily deleted when done.
#  -clone the repo into temp dir.
#  -pull & fetch all branches.
#  -jump to the branch you were on in your local machine when you launched this script.
#  -build the .zip to be uploaded to Lambda.
#      -make directory /build/collection/ to stage all the files/dirs to be zipped in.
#      -make dir /build/artifact/ to store the zipped artifact in.
#      -copy contents of /src/exe/ into collection/.
#      -create requirements file from pipfile.
#      -pip-install the requirements file libraries into collection/.
#      -zip the contents of collection/ into a .zip file in the artifact/ dir.
#          -filename ex:  function_2020-07-23T00:49:22-0700.zip
#          -timestamp is the timestamp at which it was zipped.
#  -terminate the SSH session.
#  -scp the .zip from EC2 to local laptop (example destination path:
#     trustar-aws-guard-duty/build/artifact/function_2020-07-23T00:49:22-0700.zip
#  -SSH into the EC2 instance again.
#  -delete the temp directory


branch_to_build=$(eval 'git branch --show-current')
ssh gdbuilder << EOF
sudo yum update -y
pip install --upgrade pip setuptools wheel
rm -rf temp_build
mkdir temp_build
cd temp_build
git clone git@github.com:trustar/trustar-aws-guard-duty.git
cd trustar-aws-guard-duty
git fetch --all
git pull --all
git checkout $branch_to_build
mkdir ./build
mkdir ./build/collection
mkdir ./build/artifact
cp -R ./src/exe/* ./build/collection
pipenv lock -r > requirements.txt
pipenv run pip install -r ./requirements.txt --target ./build/collection
cd build/collection/
zip -r9 ../artifact/function_$(eval 'date "+%Y-%m-%dT%H:%M:%S%z"').zip .
EOF


# Copy the artifact from the build-instance to your local laptop.
mkdir ../../build
mkdir ../../build/artifact
scp gdbuilder:temp_build/trustar-aws-guard-duty/build/artifact/* ../../build/artifact/

# Clean up build instance.
ssh gdbuilder "bash -s" < rm -rf temp_build