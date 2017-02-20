from setuptools import setup

setup(
    name='basicmodem',
    version='0.6',
    packages=['basicmodem'],
    url='https://github.com/vroomfonde1/basicmodem',
    install_requires=['pyserial'],
    license='MIT',
    author='Tim Vitz',
    author_email='timvhome@yahoo,com',
    description='A basic modem implementation for receiving caller id.',
    zip_safe=True
)
