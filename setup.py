"""PEtab test suite python package"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


def read(fname):
    with open(fname, encoding='utf-8') as f:
        return f.read()


# Get the long description from the README file
long_description = read(path.join(here, 'README.md'))

# Get the version
exec(read(path.join(here, 'petabtests', 'version.py')))

setup(
    name='petabtests',
    version=__version__,  # noqa: F821
    description='PEtab testsuite library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PEtab-dev/petab_test_suite',
    author='PEtab-dev',
    author_email='yannik.schaelte@gmail.com',
    maintainer='PEtab-dev',
    maintainer_email='yannik.schaelte@gmail.com',
    # author_email='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='PEtab testsuite',
    packages=find_packages(),
    install_requires=['numpy',
                      'pandas',
                      'petab>=0.1.4',
                      'pysb'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'petabtests_create = petabtests.core:create',
            'petabtests_clear = petabtests.core:clear',
        ]
    },
    include_package_data=True,
)
