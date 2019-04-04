from setuptools import find_packages, setup

setup(
   name='qAuth',
   version='0.1',
   description='Quantum Authentication Protocols libraries',
   author='Ravisankar A V',
   packages=find_packages(),
   include_package_data=True,
   install_requires=['simulaqron', 'cqc'],
   zip_safe=False
)