from setuptools import setup
import sys
sys.path.insert(0, ".")
from pstide import __version__

setup(
    name='pstide',
    version=__version__,
    author='Greg Pelletier',
    py_modules=['pstide'], 
    install_requires=[
        'numpy','pandas','matplotlib'
    ],
)

