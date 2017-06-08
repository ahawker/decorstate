"""
    decorstate
    ~~~~~~~~~~

    Simple "state machines" with Python decorators.

    :copyright: (c) 2015-2017 Andrew Hawker
    :license: Apache 2.0, see LICENSE for more details.
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='decorstate',
    version='0.0.3',
    description='Simple "state machines" with Python decorators',
    long_description=open('README.md').read(),
    author='Andrew Hawker',
    author_email='andrew.r.hawker@gmail.com',
    url='https://github.com/ahawker/decorstate',
    license='Apache 2.0',
    py_modules=['decorstate'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    )
)
