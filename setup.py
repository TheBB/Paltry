#!/usr/bin/env python

from setuptools import setup

setup(
    name='Paltry',
    version='1.0.0',
    description='Paltry Lisp backed by Python and LLVM',
    maintainer='Eivind Fonn',
    maintainer_email='evfonn@gmail.com',
    packages=['paltry'],
    install_requires=[
        'click',
        'llvmlite',
        'tatsu',
    ],
    entry_points={
        'console_scripts': [
            'paltry=paltry.__main__:main',
        ],
    },
)
