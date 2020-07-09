from setuptools import setup, find_packages
setup(name='trustar-guardduty',
      version='0.1.0',
      packages=find_packages(exclude=["tests"]),
      setup_requires=["setuptools-pipfile",
                      "trustar==0.3.29"],
      use_pipfile=True)
