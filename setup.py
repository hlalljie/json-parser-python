"""
    setup.py
    
    This module contains the cli setup setup for the json_validator_cli.py module.
    Included in this testing module are:
        - setup.py - unit tests for the json_validator_cli.py module

    These tests are intended to be run with pytest.

"""
from setuptools import setup, find_packages


setup(
    name="validate_json",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click",
    ],
    entry_points={
        'console_scripts': [
            'validate_json=json_validator.json_validator_cli:cli',
        ],
    },
)