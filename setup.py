from setuptools import setup, find_packages
from importlib import resources as r
import os

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name="baph",
    version="1.0.0",
    description="A python program to gather Palo Alto performance data",
    long_description=readme,
    author='John Bell',
    author_email='blue@jbell.xyz',
    url='https://github.com/packetpunter/pybaph',
    license=license,
    packages=find_packages(where="src/"),
    package_dir={"": "src"},
    #packages=find_packages(where="/"),
    install_requires= [
        'PyYAML'
    ],
    setup_requires = [
        "PyYAML"
    ]
)
