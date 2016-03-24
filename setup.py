from distutils.core import setup
setup(
  name = 'autopython',
  packages = ['autopython'],
  version = '0.1',
  description = 'Autoscripting in python 3',
  author = 'Germán Osella Massa',
  author_email = 'german.osella@nexo.unnoba.edu.ar',
  url = 'https://github.com/gosella/autopython',
  download_url = 'https://github.com/gosella/autopython',
  keywords = ['python3', 'presentation', 'autoscripting'],
  classifiers = [],
  scripts = ['autopython/autopython.py'],
  license = "GPLv3",
  install_requires=[
    "colorama",
    "Pygments",
  ],
)
