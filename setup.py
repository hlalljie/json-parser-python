from setuptools import setup, find_packages

from setuptools import setup

setup(
    name='validate_json',
    version='0.1.0',
    py_modules=['json_validator_cli'],  # Directly specify the standalone module
    package_dir={'': 'src'},  # Indicate that the module is in the 'src' directory
    include_package_data=True,
    install_requires=[
        'Click',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'validate_json=json_validator_cli:cli',  # Point to the cli function in json_validator_cli.py
        ],
    },
)
