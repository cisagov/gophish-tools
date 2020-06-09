# gophish-tools #

[![GitHub Build Status](https://github.com/cisagov/gophish-tools/workflows/build/badge.svg)](https://github.com/cisagov/gophish-tools/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/gophish-tools/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/gophish-tools?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/gophish-tools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/gophish-tools/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/gophish-tools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/gophish-tools/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/gophish-tools/develop/badge.svg)](https://snyk.io/test/github/cisagov/gophish-tools)

This repository contains a set of tools that can be used by phishing
campaign assessors to simplify the process of managing GoPhish campaigns.

## Usage ##

### PCA Assessment Docker ###

A python Docker utility for team leads to produce a JSON file containing all
configurations to run a CISA Phishing Campaign Assessment (PCA).

The PCA Assessment commands implemented in the docker container can be
aliased into the host environment by using the procedure below.

Alias the container commands to the local environment:

```console
eval "$(docker run pca-assessment)"
```

To run a GoPhish Control command:

```console
pca-assessment-builder -h
```

### Building the pca-assessment container ###

To build the Docker container for pca-assessment:

```console
docker build -t pca-assessment .
```

## Contributing ##

We welcome contributions!  Please see [here](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
