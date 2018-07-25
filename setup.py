from setuptools import setup, find_packages

setup(
    name='OTSunWebApp',
    version='0.2.2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['dill==0.2.7.1','Flask', 'otsun', 'numpy'],
    license='MIT',
    author='Gabriel Cardona',
    author_email='gabriel.cardona@uib.es',
)
