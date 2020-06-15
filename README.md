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

## Assessment JSON Field Dictionary ##

The following items are included in the assessment JSON as produced by the `pca-wizard`.
An example assessment JSON can be found [here](src/assessment/sample_assessment.json).

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| id | Assessment identifier (e.g. "RV0000"). | string | | yes |
| timezone | Timezone name based on [pytz](http://pytz.sourceforge.net/) timezones. | string | | yes |
| domain | Assessment domain for GoPhish public interface. | string | | yes |
| target_domain | Approved target domains where all email recipients must reside. | list(string) | | yes |
| start_date| Assessment start date in 24-hr ISO format with offset. | string | | yes |
| end_date | Assessment end date in 24-hr ISO format with offset. | string | | yes |
| reschedule | Indicates if the assessment json is a rescheduled assessment. | boolean | | yes |
| start_campaign | The campaign that the assessment should start at. | integer | `1` | yes |
| groups | Consolidated list of email recipients grouped to receive campaigns, [example](#group-dictionary).| list(dictionaries)  | | yes |
| pages |  GoPhish landing pages, [example](#page-dictionary).| list(dictionaries)  | | yes |
| campaigns | Assessment campaigns, [example](#campaign-dictionary). | list(dictionaries) | | yes |

### Group Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Group name in the format of `{assessment identifier}-G{integer}` (e.g. "RV0000-G1"). | string | | yes |
| targets | List of email recipients, [example](#target-dictionary). | list(dictionaries) | | yes |

### Target Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| first_name | Recipient's first name. | string | | yes |
| last_name | Recipient's last name. | string | | yes |
| email | Recipient's email address. | string | | yes |
| position | Position name for use in creating sub-groups of recipients within the organization such as HR, IT, etc. | string | | no |

### Page Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Page name in the format of `{assessment identifier}-{integer}-{descriptor}` (e.g. "RV0000-1-AutoForward"). | string | | yes |
| capture_credentials | Indicates to GoPhish if the page will forward after an action. | boolean | | yes |
| capture_passwords | Allows for capturing of user input, currently not used by PCA. | boolean | `False` | yes |
| html | Content of the landing page in HTML format. | string | | yes |

### Campaign Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Campaign name in the format of `{assessment identifier}-C{integer}` (e.g. "RV0000-C1"). | string | | yes |
| launch_date | Campaign launch date in 24-hr ISO format with offset. | string | | yes |
| completed_date | Campaign completion date in 24-hr ISO format with offset. | string | | yes |
| url | Full URL for the campaign's landing page. | string | | yes |
| page_name | Landing page name as defined in the assessment json. | string | | yes |
| group_name | Group name as defined in the assessment json. | string | | yes |
| template | Single email template for the campaign, [example](#template-dictionary). | dictionary | | yes |
| smtp | Single GoPhish sending profile, [example](#smtp-dictionary). | dictionary | | yes |

### Template Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Template name in the format of `{assessment identifier}-T{integer}-{template identifier}` (e.g. "RV0000-T1-1A2B3D"). | string | | yes |
| subject | Email subject as seen by recipients. | string | | yes |
| html | HTML representation of the email. | string | | yes |
| test | Plain text representation of the email. | string | | yes |

### SMTP Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Sending profile name in the format of `{assessment identifier}-SP-{integer}` (e.g. "RV0000-SP-1"). | string | | yes |
| from_address | From email address with display name, required format: `{display name}<{sending email address}>`. | string | | yes |
| host | Email server for GoPhish to send email through.| string | `postfix:587`| yes |
| interface_type | Type of interface GoPhish will use with mail server. | string | `SMTP` | yes |
| ignore_cert | Indicate if GoPhish should ignore certs with mail server. | boolean | `True` | yes |

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
