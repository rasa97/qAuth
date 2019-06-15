from setuptools import find_packages, setup

setup(
   name='qAuth-rasa97',
   version='0.0.1',
   description='Quantum Authentication Protocols libraries',
   author_email="rasa97uchiha@gmail.com",
   author='Ravisankar A V',
   packages=find_packages(),
   include_package_data=True,
   install_requires=['simulaqron==2.1.1', 'cqc==2.1.0'],
   zip_safe=False
)