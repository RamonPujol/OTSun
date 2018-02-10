from setuptools import setup, find_packages

setup(
    name='WebAppSunScene',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask','pysunscene'],
    license = 'MIT',
    author = 'Gabriel Cardona',
    author_email = 'gabriel.cardona@uib.es',
)

