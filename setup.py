"""Installation with setuptools or pip."""
from setuptools import setup, find_packages
import os
import ast


def get_version_from_init():
    """Obtain library version from main init."""
    init_file = os.path.join(
        os.path.dirname(__file__), 'zgoubidoo', '__init__.py'
    )
    with open(init_file) as fd:
        for line in fd:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=', 1)[1].strip())


with open('README.md') as f:
    readme = f.read()

with open('COPYING') as f:
    lic = f.read()


setup(
    name='zgoubidoo',
    version=get_version_from_init(),
    description='Zgoubidoo: a Python interface for Zgoubi.',
    long_description=readme,
    author='Cédric Hernaslteens',
    author_email='cedric.hernalsteens@iba-group.com',
    url='https://github.com/chernals/zgoubidoo',
    license=lic,
    packages=find_packages(exclude=('tests', 'docs', 'examples')),
    install_requires=[
        'numba',
        'numpy>=1.14.0',
        'pandas>=0.22.0',
        'scipy>=1.0.0',
        'pint',
        'matplotlib',
        'numpy-quaternion',
        'plotly',
        'numpy-stl',
    ],
    package_data={'zgoubidoo': []},
)
