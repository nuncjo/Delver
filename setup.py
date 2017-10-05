# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def long_description():

    def read_markdown(file):
        try:
            from pypandoc import convert
            return convert(file, 'rst')
        except (ImportError, OSError):
            with open(file) as readme:
                return readme.read()

    readme = read_markdown('README.md')
    with open('HISTORY.rst') as history_file:
        history = history_file.read()
        return '\n\n'.join((readme, history))


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
    version='0.1.6',
    description="Modern user friendly web automation and scraping library.",
    long_description=long_description(),
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
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
