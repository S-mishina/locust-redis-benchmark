from setuptools import setup, find_packages
import os

URL = 'https://github.com/S-mishina/locust-cache-benchmark'
AUTHOR = 'S-mishina'

with open(os.path.join(os.path.dirname(__file__), 'cache_benchmark', 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    author=AUTHOR,
    url=URL,
    name='locust-cache-benchmark',
    packages=find_packages(where="cache_benchmark/src"),
    package_dir={"": "cache_benchmark/src"},
    install_requires=requirements,
    include_package_data=True,
    version='1.0.0',
    entry_points={
        'console_scripts': [
            'locust_cache_benchmark = cache_benchmark.main:main'
        ]
    }
)
