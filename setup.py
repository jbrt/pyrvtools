from setuptools import setup

def readme():
    with open('README.rst') as fh:
        return fh.read()

setup(
    name='pyrvtools',
    version='1.0.1',
    packages=['pyrvtools'],
    install_requires=['xlrd'],
    url='https://github.com/jbrt/pyrvtools',
    license='GPL',
    author='Julien B.',
    author_email='julien@toshokan.fr',
    description='Extract useful information from an RVTools ESX inventory file',
    long_description=readme(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
