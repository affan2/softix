from setuptools import setup

requirements = ('requests')
setup(
    name='softix',
    packages=['softix'],
    version='0.0.2',
    author='Matt Chung',
    author_email='matt@itsmemattchung.com',
    description='Python client library to interface with Dubai ticketing API',
    install_requires=requirements,
)
