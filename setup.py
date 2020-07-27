from setuptools import setup, find_packages  # noqa: H301

NAME = "remote-sqlitedict"
VERSION = "0.4.2"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "plumbum==1.6.9",
    "rpyc==4.1.5",
    "sqlitedict==1.6.0"
]


setup(
    name=NAME,
    version=VERSION,
    description="Remote sqlitedict",
    author_email="",
    url="",
    keywords=["sqlitedict", "rpyc", "remote"],
    install_requires=REQUIRES,
    py_modules=['remote_sqlitedict'],
    include_package_data=True,
    long_description="""\
    This package allows for a remote access to SQLite backed dictionary for data persistence   # noqa: E501
    """
)
