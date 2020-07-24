# EC-2 "BUILD" INSTANCE ONE-TIME-SETUP SCRIPT.
# Does: Sets up Python 3.7.7 venv on an AmazonLinux2 EC-2 instance.
#
# Pre-Reqs:
#  -create a new amazonlinux2 EC2 instance.
#  -create a new GitHub SSH key and install it in your user account on the EC2 instance.
#    (that host will need to be able to clone this git repo)
#  -in SSH config file on your laptop, make an entry named "gdbuilder" that will
#   SSH you into the EC2 instance to a user account that has "sudo".  (usually 'ec2-user')
#
# This script will:
#  -install c-compiler toolchain.
#  -install pyenv
#  -use pyenv to install Python 3.7.7.
#
# Run this from your personal laptop.  It will SSH to the instance and do the
# work.
#
# Ref:  https://gist.github.com/mrthomaskim/e48d747816cfac0b481684e7a5084e48
#
# If script fails,



setup() {
    cd ~

    # Apply all amazonlinux updates.
    sudo yum update -y

    # C toolchain.
    sudo yum groupinstall "Development Tools"

    # Dependencies for building python interpreter from source.
    sudo yum install -y openssl-devel readline-devel zlib-devel

    # clone Pyenv to '~/.pyenv' directory.
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv

    # make Pyenv accessible from CLI.
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
    source ~/.bash_profile

    # use Pyenv to download/build/install a Python 3.7.7 base environment.
    pyenv install 3.7.7

    # make Python 3.7.7 the default interpreter to be used anytiime you call
    # "python ____.py" from the CLI.
    pyenv global 3.7.7

    # update "pip" and "setuptools".
    pip install --upgrade pip setuptools

    # install "pipenv" to "user site packages" location (~/.local/)
    pip install pipenv --user

    # Need to run this every time you add new python versions or pyenv-virtualenvs.
    pyenv rehash
}

ssh gdbuilder "bash -s" < setup