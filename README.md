TARGET AUDIENCE.

This repo is intended for developer use.  It contains source code that needs to
go through a "build" process to construct an artifact (.zip) that can be uploaded
to Lambda.


OVERVIEW / CONTENTS.

- Software you should already have on your laptop.

- Pyenv particulars.

- Software your laptop needs specifically for this project.
   - Python 3.7.7
   - Pipenv
   - a virtual env. (created by Pipenv, not Pyenv)
   
- Testing the source code.
   - Configs.
   - Test case.
   
- Building the artifact.
   - initializing the EC2 build host.
   - building the artifact.



SOFTWARE YOU SHOULD ALREADY HAVE ON YOUR LAPTOP (OS X).

- Homebrew package manager  (follow Homebrew's installation docs.)

- GNU C Compiler that Pyenv will use to compile Python interpreter versions
    - recommend:  brew install gcc@9 >= 9.3.0
    - OS X usually comes with an older version of the Clang C Compiler.
        I usually experience less trouble compiling Python interpreters with
        GCC than with Clang.
    - When you use Brew to install both gcc@9 and Pyenv, Pyenv will always use 
       the gcc@9 compiler you brew-installed when it compiles a new Python 
       interpreter version.  You do not have to symlink gcc into your path for 
       this behavior to take place.  This is nice because you can leave OS X's 
       CLang as the default C Compiler for your laptop but know that your Python
       interpreters will always be compiled using a recent version of the GNU 
       C Compiler. 
    

- Python compilation dependencies.
    * It's likely fine to use your Mac's default versions.  If you experience
    difficulties while Pyenv builds interpreter versions, try brew-installing
    the latest versions of these projects and sym-linking them appropriately.
    - openssl >= 1.1.1g
    - readline >= 8.0.4
    - zlib >= 1.2.11
    - sqlite >= 3.32.3

- Pyenv  (install from Homebrew)
    - Pyenv is a set of bash scripts that automate the process of cloning 
       python source from github and building it using your brew-installed 
       gcc@9 and openssl. 


PYENV PARTICULARS:
- TruSTAR uses Pipenv for virtual environment management for all of its Python
    code.

- Running "pipenv virtualenv-xxxx" commands while you have a "pyenv virtualenv"
    active can be confusing and lead to errors.

- Do not activate any virtual environments you may have created with the
    "pyenv virtualenv" plugin while working with this repo.  Deactivate them, 
    and make sure that typing "python" from the CLI from any working directory
    will use an intepreter installed/built by Pyenv.  (avoid using your Mac's 
    system interpreters found in the system libraries and/or the XCode 
    developer tools.)

- Do not pip-install Pipenv into a virtual environment created by the
    "pyenv virtualenv" plugin.  (see instructions for installing pipenv below.)



SOFTWARE PRE-REQS FOR THIS PROJECT:

- Python 3.7.7 interpreter.

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
        by adding it to my "bash_profile" file and then "source" 'ing that file
        using these commands:
        
            $ echo 'export PATH=/Users/S/.local/bin:$PATH' >>~/.bash_profile
            $ source ~/.bash_profile

    - Verify that the Pipenv executable is now in your path.

            $ which pipenv
            /Users/S/.local/bin/pipenv


- Virtual Environment

    - Navigate your terminal session to the root dir of this repo.

    - USE PIPENV to create a virtual environment for this project according
        to the preferences specified in the Pipfile.  This will automatically 
        install the necessary Python interpreter versions if they don't yet 
        exist on your laptop, make a virtual environment for this project 
        for each interpreter version, and it will install the Python libraries
        specified in the Pipfile into each virtual environment it creates.   
                
                $ pipenv install --dev


IDE SETUP:

- IDE should execute trustar-aws-guard-duty/tests/test.py using your virtual
   env interpreter and a current working directory of
   trustar-aws-guard-duty/tests.
   
- To find the path to your virtual environment's Python interpreter executable
   for the virtual environment created by Pipenv:  
   
      $ pipenv --py
      /Users/S/.local/share/virtualenvs/trustar-aws-guard-duty-rfxu9yTj/bin/python

   Tell your IDE that it should launch test.py with the interpreter found at 
   the location returned by this command. 


TESTING:

- see "IDE SETUP" above.

- Configs can be entered into trustar-aws-guard-duty/tests/private/test.conf,
   and the test.conf.spec file shows the options you need to fill out.

- Didn't implement Pytest in this project, out of time.

- Note, the test does require an internet connection.

- The test is "end-to-end" in nature.  It grabs a sample GuardDuty Finding
   dictionary from file and sends that dictionary into the lambda handler.  
   After the lambda handler submits a TruSTAR report to the enclave, the test
   will fetch the report from the enclave and checks that it is equal to the 
   report that the test expects to retrieve.  

BUILDING:

- Create an Amazonlinux2 EC2 instance.

- Create stanza in laptop's SSH config file for the instance.

        Host gdbuilder    <-- Important to use "gdbuilder" exactly.
          User ec2-user
          HostName 13.57.247.46  <--REPLACE WITH YOUR INSTANCE'S IP.
          IdentityFile ~/.ssh/gdlambdabuilder.pem  <-- SSH Key issued by AWS.

    - The setup and build scripts in this repo's scripts/ dir are hard-coded to 
       SSH to "gdbuilder", so having that stanza in your SSH config file 
       use that precise identifier for the "Host" is critical to those scripts
       working properly. 
       
- Create a new Github SSH key for your account on that instance.

    - Follow directions on Github's site.  In general:

        - SSH from your laptop into the EC2 host.
        - Create new SSH cert on the host.
        - Add the cert to your Github account.

- EC-2 "Build Instance" First-time-setup.
    - From your local laptop, run 
    scripts/ec2_build_instance_one-time-setup/ec2_build_instance_one-time-setup.sh
    - The documentation in that script explains what it does.  
    
- Building.
    - Run the "build_artifact....." script from your local laptop.
    - The documentation in that script explains what it does.  
    - The resulting artifact will end up in your local laptop's 
       "trustar-aws-guard-duty/build/artifact" directory.