# Run this after running "amzn_linux_pyenv_install.sh".
# Run this from AmazonLinux2 EC-2 instance while SSHed in as a user with "sudo" priivs.
# Run this with CWD being the directory this script resides in.
mkdir ../../build
cp -R ../src/* ../../build/
pip install -r ../requirements.txt --target ../../build
zip -r9 ../../function.zip ../../build/.