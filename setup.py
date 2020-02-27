"""PEtab test suite python package"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='petabtests',
    version='0.0.0a1',
    description='PEtab testsuite library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PEtab-dev/petab_test_suite',
    author='PEtab-dev',
    # author_email='',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish
        'License :: OSI Approved :: BSD 3-Clause "New" or "Revised"'
        ' License (BSD-3-Clause)',

        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='PEtab testsuite',
    packages=find_packages(where='petab_test_suite'),
    python_requires='>=3.7',
    # install_requires=[''],
    entry_points={
        'console_scripts': [
            'petab_test_suite_create = petabtests.core:main',
        ]
    },

)
