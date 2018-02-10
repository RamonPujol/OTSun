from distutils.core import setup

setup(
    name='webappSunScene',
    version='0.1',
    py_modules=['webappsunscene'],
    packages = ['utils','experiments','experiments.utils'],
    url='',
    license='MIT',
    author='Gabriel Cardona, Ramon Pujol',
    author_email='gabriel.cardona@uib.es, ramon.pujol@uib.es',
    description='',
    install_requires=[
        'pysunscene>=0.9.5',
    ]
)
