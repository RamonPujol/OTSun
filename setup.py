from distutils.core import setup

setup(
    name='webappSunScene',
    version='0.1',
    packages = ['webappsunscene',
                'webappsunscene.experiments',
                'webappsunscene.processors',
                'webappsunscene.utils'],
    # package_data = {
    #     'experiments': ['data/*'],
    #     'webappsunscene': ['templates/*']
    # },
    url='',
    license='MIT',
    author='Gabriel Cardona, Ramon Pujol',
    author_email='gabriel.cardona@uib.es, ramon.pujol@uib.es',
    description='',
)
