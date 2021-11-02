#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = [open('requirements.txt').read().split()]
setup_requirements = [open('requirements.txt').read().split()]

from blackref import (__description__, __version__, __author__,
                      __email__, __summary__, __license__)

test_requirements = []

setup(
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description=__summary__,
    install_requires=requirements,
    license=__license__,
    long_description=__description__,
    include_package_data=True,
    keywords=['code formattig', 'latex', 'bibtex', 'biblatex'],
    name='blackref',
    packages=find_packages(where='.'),
    #    scripts=['blackref.py'],
    entry_points={
        'console_scripts': [
            'blackref = blackref.__init__:main'
        ]},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dvolgyes/blackref',
    version=__version__,
    zip_safe=False,
    python_requires='>=3.6',
)
