from setuptools import setup
setup(
  name = 'autopython',
  packages = ['autopython'],
  version = '0.1',
  description = 'Autoscripting for Python 3',
  author = 'Germán Osella Massa',
  author_email = 'german.osella@nexo.unnoba.edu.ar',
  url = 'https://github.com/gosella/autopython',
  download_url = 'https://github.com/gosella/autopython',
  keywords = ['python3', 'presentation', 'autoscripting'],
  classifiers = [],
  scripts = ['bin/autopython'],
  maintainer = 'Germán Osella Massa',
  maintainer_email = 'german.osella@nexo.unnoba.edu.ar',
  data_files = ['autopython/core.py', 'autopython/console.py', 'autopython/script_parser.py'],
  license = "GPLv3",
  install_requires=[
    "colorama",
    "Pygments",
  ],
)
