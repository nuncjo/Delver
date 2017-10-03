#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'lxml',
    'cssselect'
]

setup_requirements = [
    # TODO(nuncjo): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='delver',
    version='0.1.3',
    description="Modern user friendly web automation and scraping library.",
    long_description=readme + '\n\n' + history,
    author="Nuncjo",
    author_email='zoreander@gmail.com',
    url='https://github.com/nuncjo/delver',
    packages=find_packages(include=['delver']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='delver, web automation, spider, scraper, mechanize, scrapy, robobrowser',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
