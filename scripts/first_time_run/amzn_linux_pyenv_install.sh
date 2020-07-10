# Sets up Python 3.7.7 venv on an AmazonLinux2 EC-2 instance.
# Run this on an AmazonLinux EC-2 instance under a user with "sudo" privs.
# Ref:  https://gist.github.com/mrthomaskim/e48d747816cfac0b481684e7a5084e48

cd ~
sudo yum groupinstall "Development Tools"
git --version
gcc --version
bash --version
python --version   # system python version.
sudo yum install -y openssl-devel readline-devel zlib-devel
sudo yum update

### install `pyenv`
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile

### restart SHELL and install `python`
echo $PATH
echo $(pyenv root)
pyenv install --list
pyenv install 3.7.7
pyenv versions

### install `pyenv virtualenv`
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile

### restart SHELL and virtualenv
pyenv virtualenv 3.7.7 default-3.7.7
pyenv virtualenvs
pyenv local default-3.7.7
pyenv version
cat .python-version
pyenv rehash

python --version
pip list --format=columns

EOF