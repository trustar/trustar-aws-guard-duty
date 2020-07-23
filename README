TARGET AUDIENCE:
This repo is intended for developer use.  It contains source code that needs to
go through a "build" process to construct an artifact (.zip) that can be uploaded
to Lambda.


OVERVIEW / CONTENTS:
-Software you should already have on your laptop.
-Pyenv particulars.
-Software your laptop needs specifically for this project.
   -Python 3.7.7
   -Pipenv
   -a virtual env.
-Testing the source code.
   -Configs.
   -Test case.
-Building the artifact.
   -initializing the EC2 build host.
   -building the artifact.



SOFTWARE YOU SHOULD ALREADY HAVE ON YOUR LAPTOP:
- Homebrew package manager  (follow Homebrew's installation docs.)
- GNU C Compiler that Pyenv will use to compile Python interpreter versions
    - recommend:  brew install gcc@9 >= 9.3.0
    - OS X usually comes with an older version of the Clang C Compiler.
        I usually experience less trouble compiling Python interpreters with
        GCC than with Clang.
- Python compilation dependencies
    * It's likely fine to use your Mac's default versions.  If you experience
    difficulties while Pyenv builds interpreter versions, try brew-installing
    the latest versions of these projects and sym-linking them appropriately.
    - openssl >= 1.1.1g
    - readline >= 8.0.4
    - zlib >= 1.2.11
    - sqlite >= 3.32.3
- Pyenv  (install from Homebrew)


PYENV PARTICULARS:
- TruSTAR uses Pipenv for virtual environment management.
- Running "pipenv virtualenv-xxxx" commands while you have a "pyenv virtualenv"
    active can be confusing.
- Do not activate any virtual environments you may have created with the
    "pyenv virtualenv" plugin.
- Do not pip-install Pipenv into a virtual environment created by the
    "pyenv virtualenv" plugin.



SOFTWARE PRE-REQS FOR THIS PROJECT:
- Python 3.7.7
    - use Pyenv to install this.

          $ pyenv install 3.7.7

    - recommend setting this as your Pyenv global interpreter, which means
       this will be the interpreter you use by default when not inside a
       virtual environment.

          $ pyenv global 3.7.7


- Pipenv
    - use the 3.7.7 interpreter's primary environment (NOT a virtual environment
       spawned from that interpreter) to pip-install Pipenv to your user
       site packages directory

          $ pip install pipenv --user


    - Find your "user site packages" directory.

          $ python -m site
          $ python -m site
          sys.path = [
              '/Users/S',
              '/Users/S/.pyenv/versions/3.7.7/lib/python37.zip',
              '/Users/S/.pyenv/versions/3.7.7/lib/python3.7',
              '/Users/S/.pyenv/versions/3.7.7/lib/python3.7/lib-dynload',
              '/Users/S/.local/lib/python3.7/site-packages',
              '/Users/S/.pyenv/versions/3.7.7/lib/python3.7/site-packages',
          ]
          USER_BASE: '/Users/S/.local' (exists)
          USER_SITE: '/Users/S/.local/lib/python3.7/site-packages' (exists)
          ENABLE_USER_SITE: True


    - The "pipenv" executable script is placed in  '/Users/S/.local/bin'.  Make
        sure that that directory is in your PATH.

            $ python -c "import os; print(os.environ['PATH'].replace(':', '\n'))"
            /Users/S/.pyenv/versions/3.7.7/bin
            /usr/local/Cellar/pyenv/1.2.19/libexec
            /Users/S/.pyenv/shims
            /Users/S/.pyenv/bin
            /Users/S/.local/bin
            /Users/S/.pyenv/shims
            /Users/S/.pyenv/bin
            /Users/S/.local/bin
            /Users/S/.pyenv/shims
            /Users/S/.pyenv/bin
            /Users/S/.local/bin
            /usr/local/bin
            /usr/local/Cellar
            /usr/bin
            /bin
            /usr/sbin
            /sbin
            /Applications/VMware Fusion.app/Contents/Public
            /opt/X11/bin
            /Library/Apple/usr/bin


    - If /Users/S/.local/bin were not in my path, I would add it to my path
        using these commands:

            $ echo 'export PATH=/Users/S/.local/bin:$PATH' >>~/.bash_profile


    - Verify that the Pipenv executable is now in your path.

            $ which pipenv
            /Users/S/.local/bin/pipenv


- Virtual Environment
    - Navigate your terminal session to the root dir of this repo.
    - USE PIPENV to create a virtual environment for this project according
        to the preferences specified in the Pipfile.

        $ pipenv --python 3.7.7


    - install all development dependencies into this virtual env.

        $ pipenv install --dev


IDE SETUP:
- IDE should execute trustar-aws-guard-duty/tests/test.py using your virtual
   env interpreter and a current working directory of
   trustar-aws-guard-duty/tests.


TESTING:
- see "IDE SETUP" above.
- Configs can be entered into trustar-aws-guard-duty/tests/private/test.conf,
   and the test.conf.spec file shows the options you need to fill out.
- Didn't implement Pytest in this project, out of time.


BUILDING:
- Create Amazonlinux2 EC2 instance.
- Create stanza in laptop's SSH config file for the instance.

        Host gdbuilder    <-- Important to use "gdbuilder" exactly.
          User ec2-user
          HostName 13.57.247.46  <--REPLACE WITH YOUR INSTANCE'S IP.
          IdentityFile ~/.ssh/gdlambdabuilder.pem  <-- SSH Key issued by AWS.

- Create a new Github SSH key for your account on that instance.
    - Follow directions on Github's site.
        - SSH into host.
        - Create new SSH cert on the host.
        - Add the cert to your Github account.
- First-time-setup.
    - SSH into host.
    - clone this repo to the build host.
    - Run scripts/ec2_build_instance_one-time-setup/ec2_build_instance_one-time-setup.sh
    - delete the repo from the build host.
- Building.
    - Run the "build_artifact....." script from your local laptop.