__name__ = 'decorstate'
__version__ = '0.0.1'
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name=__name__,
    version=__version__,
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
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    )
)
