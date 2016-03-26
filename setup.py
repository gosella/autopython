from setuptools import setup

with open( 'README.md' ) as readme_file:
    long_description = readme_file.read()

setup(
  name = 'autopython',
  version = '0.2',
  description = 'Autoscripting for Python 3',
  long_description = long_description,

  packages = ['autopython'],
  scripts = ['bin/autopython'],
  install_requires=[
    "colorama",
    "Pygments",
  ],
  
  url = 'https://github.com/gosella/autopython',
  download_url = 'https://github.com/gosella/autopython',
  license = "GPLv3",
  keywords = ['python3', 'presentation', 'autoscripting'],
  classifiers = [],
  author = 'Germán Osella Massa',
  author_email = 'german.osella@nexo.unnoba.edu.ar',
  maintainer = 'Germán Osella Massa',
  maintainer_email = 'german.osella@nexo.unnoba.edu.ar',
)
