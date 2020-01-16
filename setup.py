from setuptools import setup, find_packages

setup(
    name='pca-assessment',
    version='0.0.1',
    author='Bryce Beuerlein',
    author_email='bryce.beuerlein@hq.dhs.gov',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/pca-assessment-builder',
             'bin/pca-assessment-builder'],
    license='LICENSE.txt',
    description='PCA Assessment JSON Build Script',
    long_description=open('README.md').read(),
    install_requires=[
        "docopt >= 0.6.2",
        "prompt-toolkit == 2.0.9",
        "pytz >= 2019.1",
        "pytest",
        "ipython"
    ]
)