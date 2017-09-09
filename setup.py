from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

VERSION = '0.1.0'
# TODO: version should be generated

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(
    name='PyYADL',
    version=VERSION,
    description='Yet another distributed lock for python',
    long_description=long_description,
    url='https://github.com/PawelJ-PL/PyYADL',
    author='Pawel',
    author_email='inne.poczta@gmail.com',
    license='MIT',
    keywords='distributed lock Redis implementation',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=['redis'],
    extras_require={
        'test': ['coverage'],
    },
    python_requires='>=3',

)
