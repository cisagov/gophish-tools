"""
This is the setup module for the gophish-tools project.

Based on:

- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""

# Standard Python Libraries
from glob import glob
from os.path import basename, splitext

# Third-Party Libraries
from setuptools import find_packages, setup


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()


def package_vars(version_file):
    """Read in and return the variables defined by the version_file."""
    pkg_vars = {}
    with open(version_file) as f:
        exec(f.read(), pkg_vars)  # nosec
    return pkg_vars


setup(
    name="gophish-tools",
    # Versions should comply with PEP440
    version=package_vars("src/assessment/_version.py")["__version__"],
    description="Helpful tools for interacting with GoPhish",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # NCATS "homepage"
    url="https://www.us-cert.gov/resources/ncats",
    # The project's main homepage
    download_url="https://github.com/cisagov/gophish-tools",
    # Author details
    author="Cyber and Infrastructure Security Agency",
    author_email="ncats@hq.dhs.gov",
    license="License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.7",
    # What does your project relate to?
    keywords="gophish automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # package_data={"": extra_files},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=[
        "docopt >= 0.6.2",
        "prompt-toolkit == 2.0.9",
        "pytz >= 2019.1",
        "httpagentparser",
        "setuptools >= 24.2.0",
        "schema",
        # GoPhish Requirements
        "appdirs>=1.4.0",
        "packaging==16.8",
        "pyparsing==2.1.10",
        "python-dateutil==2.6.0",
        "requests>=2.20.0",
        "six==1.10.0",
        # Script Requirements
        "gophish >= 0.2.5",
    ],
    extras_require={
        "test": [
            "pre-commit",
            # coveralls 1.11.0 added a service number for calls from
            # GitHub Actions. This caused a regression which resulted in a 422
            # response from the coveralls API with the message:
            # Unprocessable Entity for url: https://coveralls.io/api/v1/jobs
            # 1.11.1 fixed this issue, but to ensure expected behavior we'll pin
            # to never grab the regression version.
            "coveralls != 1.11.0",
            "coverage",
            "pytest-cov",
            "mock",
            "pytest",
        ]
    },
    # Conveniently allows one to run the CLI tools
    entry_points={
        "console_scripts": [
            "gophish-complete = tools.gophish_complete:main",
            "gophish-export = tools.gophish_export:main",
            "gophish-import = tools.gophish_import:main",
            "gophish-test = tools.gophish_test:main",
            "gophish-cleaner = tools.gophish_cleaner:main",
            "pca-wizard = assessment.builder:main",
            "pca-wizard-templates = templates.generate_template:main",
            "pca-assessment-reschedule = assessment.reschedule:main",
        ]
    },
)
