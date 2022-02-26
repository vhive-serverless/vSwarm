from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
   name='tracing',
   version='0.1',
   description='Zipkin Tracing',
   author='EASE-lab',
#    packages=['tracing'],  # would be the same as name
   install_requires=install_requires, #external packages acting as dependencies
)