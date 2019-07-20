from setuptools import setup, find_packages
import versioneer

setup(
    name='OTSunWebApp',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'otsun', 'numpy', 'autologging'],
    license='MIT',
    author='Gabriel Cardona',
    author_email='gabriel.cardona@uib.es',
)
