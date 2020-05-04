from setuptools import setup, find_packages

setup(
    name="pca-assessment",
    version="0.0.2",
    author="Bryce Beuerlein",
    author_email="bryce.beuerlein@hq.dhs.gov",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=["bin/pca-builder", "bin/pca-reschedule", "bin/gophish-import"],
    license="LICENSE.txt",
    description="PCA Assessment JSON Build Script",
    long_description=open("README.md").read(),
    install_requires=[
        "docopt >= 0.6.2",
        "prompt-toolkit == 2.0.9",
        "pytz >= 2019.1",
        "pytest",
        "ipython",
        # GoPhish Requirements
        "appdirs==1.4.0",
        "packaging==16.8",
        "pyparsing==2.1.10",
        "python-dateutil==2.6.0",
        "requests>=2.20.0",
        "six==1.10.0",
        # Script Requirements
        "gophish >= 0.2.5",
    ],
)
