from setuptools import setup
setup(
  name = 'autopython',
  packages = ['autopython'],
  version = '0.0.1',
  description = 'Autoscripting in python 3',
  author = 'Germán Osella Massa',
  author_email = 'german.osella@nexo.unnoba.edu.ar',
  url = 'https://github.com/gosella/autopython',
  download_url = 'https://github.com/gosella/autopython',
  keywords = ['python3', 'presentation', 'autoscripting'],
  classifiers = [],
  scripts = ['bin/autopython'],
  maintainer = 'Federico Gonzalez',
  maintainer_email = 'federicogonzalez761@gmail.com',
  data_files = ['autopython/autopython.py', 'autopython/console.py', 'autopython/script_parser.py'],
  license = "GPLv3",
  install_requires=[
    "colorama",
    "Pygments",
  ],
)
