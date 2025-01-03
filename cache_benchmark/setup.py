from setuptools import setup, find_packages

URL = 'https://github.com/S-mishina/locust-cache-benchmark'
AUTHOR = 'S-mishina'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    author=AUTHOR,
    url=URL,
    name='locust-cache-benchmark',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    include_package_data=True,
    version='1.0.0'
)
