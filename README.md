# gophish-tools #

[![GitHub Build Status](https://github.com/cisagov/gophish-tools/workflows/build/badge.svg)](https://github.com/cisagov/gophish-tools/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/gophish-tools/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/gophish-tools?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/gophish-tools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/gophish-tools/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/gophish-tools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/gophish-tools/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/gophish-tools/develop/badge.svg)](https://snyk.io/test/github/cisagov/gophish-tools)

## Docker Image ##

![MicroBadger Layers](https://img.shields.io/microbadger/layers/cisagov/gophish-tools)
![Docker Image Size](https://img.shields.io/docker/image-size/cisagov/gophish-tools)

This repository contains a set of scripts that can be used by phishing
campaign assessors to simplify the process of managing GoPhish campaigns.

## Scripts ##

* `gophish-cleaner` - Removes an assessment or elements of an assessment
  in GoPhish.
* `gophish-complete` - Completes a campaign in GoPhish and/or outputs a
  GoPhish campaign summary.
* `gophish-export` - Exports all the data from an assessment within GoPhish
  into a single JSON file. In addition, user report JSONs for each campaign in
  an assessment will also be generated, for later import into the PCA database.
* `gophish-import` - Imports an assessment JSON file into GoPhish.
* `gophish-test` - Sends a duplicate assessment from GoPhish to custom
  targets as a test.
* `pca-wizard` - Creates an assessment JSON file via an interactive "wizard".
* `pca-wizard-templates` - Generates templates for files needed when creating
  an assessment JSON with `pca-wizard`.

## Usage ##

The scripts in this project can be executed either in a local Python
environment or in a Docker container.

### Install and run via local Python ###

We strongly encourage the use of virtual Python environments.  Please see
[this section](CONTRIBUTING.md#installing-and-using-pyenv-and-pyenv-virtualenv)
in our ["Contributing" document](CONTRIBUTING.md) for information on how
to set up and use a virtual Python environment.

To install the scripts in your local Python environment:

```console
git clone https://github.com/cisagov/gophish-tools.git
cd gophish-tools
pip install --requirement requirements.txt
```

After the scripts have been installed, they can be run like any other script:

```console
gophish-import
```

### Pull or build Docker image ###

Pull `cisagov/gophish-tools` from the Docker repository:

```console
docker pull cisagov/gophish-tools
```

Or build `cisagov/gophish-tools` from source:

```console
git clone https://github.com/cisagov/gophish-tools.git
cd gophish-tools
docker build --tag cisagov/gophish-tools .
```

### Run scripts via Docker ###

The easiest way to use the containerized scripts is to alias them in your
local shell:

```console
eval "$(docker run cisagov/gophish-tools)"
```

That will add aliases to your **current shell** for all of the
[scripts](#scripts) mentioned above, plus an additional one for
`gophish-tools-bash`, which can be used to start up a `bash` shell inside
a `gophish-tools` container.

## Assessment JSON Field Dictionary ##

The following items are included in the assessment JSON as produced by
`pca-wizard`.
An example assessment JSON can be found [here](src/assessment/sample_assessment.json).

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| id | Assessment identifier. (e.g. "RV0000") | string | | yes |
| timezone | Timezone name based on [pytz](http://pytz.sourceforge.net/) timezones. (e.g. "US/Eastern") | string | | yes |
| domain | Assessment domain for GoPhish public interface. (e.g. "domain.tld") | string | | yes |
| target_domain | Approved target domains where all email recipients must reside. (e.g. ["target1.tld", "target2.tld"]) | list(string) | | yes |
| start_date | Assessment start date in 24-hr ISO format with offset. (e.g. "2020-01-01T14:00:00-04:00") | string | | yes |
| end_date | Assessment end date in 24-hr ISO format with offset. (e.g. "2020-01-06T15:30:00-04:00") | string | | yes |
| reschedule | Indicates if the assessment json is a rescheduled assessment. | boolean | | yes |
| start_campaign | The campaign that the assessment should start at. | integer | `1` | no |
| groups | Consolidated list of email recipients grouped to receive campaigns, [example](#group-dictionary). | list(dict) | | yes |
| pages | GoPhish landing pages, [example](#page-dictionary). | list(dict) | | yes |
| campaigns | Assessment campaigns, [example](#campaign-dictionary). | list(dict) | | yes |

### Group Dictionary ###

Groups are imported from a templated `csv` file that can be generated
with the command `pca-wizard-templates  --targets`.

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Group name in the format of `{assessment identifier}-G{integer}` (e.g. "RV0000-G1"). | string | | yes |
| targets | List of email recipients, [example](#target-dictionary). | list(dict) | | yes |

### Target Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| first_name | Recipient's first name. | string | | yes |
| last_name | Recipient's last name. | string | | yes |
| email | Recipient's email address. (e.g. "john.doe@target1.tld") | string | | yes |
| position | Position name for use in creating sub-groups of recipients within the organization such as "HR", "IT", etc. | string | | no |

### Page Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Page name in the format of `{assessment identifier}-{integer}-{descriptor}` (e.g. "RV0000-1-AutoForward"). | string | | yes |
| capture_credentials | Capture all non-password input with GoPhish. Supports forwarding after submit action. | boolean | | yes |
| capture_passwords | Capture password input by the user, but note that captured input is **stored in plain text as of GoPhish version 0.9.0.** | boolean | `False` | no |
| html | Content of the landing page in HTML format. | string | | yes |

### Campaign Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Campaign name in the format of `{assessment identifier}-C{integer}` (e.g. "RV0000-C1"). | string | | yes |
| launch_date | Campaign launch date in 24-hr ISO format with offset. (e.g. "2020-01-01T14:00:00-04:00")  | string | | yes |
| completed_date | Campaign completion date in 24-hr ISO format with offset. (e.g. "2020-01-01T15:30:00-04:00")  | string | | yes |
| url | Full URL for the campaign's landing page. (e.g. "http://domain.tld/camp/1") | string | | yes |
| page_name | Landing page name as defined in the assessment json. | string | | yes |
| group_name | Group name as defined in the assessment json. | string | | yes |
| template | Email template for the campaign, [example](#email-template-dictionary). | dict | | yes |
| smtp | GoPhish sending profile, [example](#smtp-dictionary). | dict | | yes |

### Email Template Dictionary ###

Email templates can be imported from a templated `json` file that can be be generated
with the command `pca-wizard-templates  --emails`.

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Template name in the format of `{assessment identifier}-T{integer}-{template identifier}` (e.g. "RV0000-T1-1A2B3D"). | string | | yes |
| subject | Email subject as seen by recipients. | string | | yes |
| html | HTML representation of the email. | string | | yes |
| text | Plain text representation of the email. | string | | yes |

### SMTP Dictionary ###

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| name | Sending profile name in the format of `{assessment identifier}-SP-{integer}` (e.g. "RV0000-SP-1"). | string | | yes |
| from_address | From email address with display name, required format: `{display name}<{sending email address}>`. (e.g. "John Doe\<john.doe@domain.tld\>") | string | | yes |
| host | Email server for GoPhish to send email through. | string | "postfix:587" | no |
| interface_type | Type of interface GoPhish will use with mail server. | string | "SMTP" | no |
| ignore_cert | Indicate if GoPhish should ignore certs with mail server. | boolean | `True` | no |

## User Report Field Dictionary ##

User report JSONs are also exported by `gophish-export`. User reports
summarize data from targeted user clicks on phishing emails generated by a
campaign. These JSON files are later imported into the PCA database.

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-------:|:--------:|
| assessment | Assessment ID that this user report is associated with. | string | | yes |
| campaign | Campaign ID that this user report is associated with. | string | | yes |
| customer | Customer ID that this user report document is associated with. Note that Gophish does not contain this information, so `gophish-export` will always export it as `null`. | string | `null` | no |
| first_report | First report (click) generated by a targeted user. Format: "YYYY-MM-DDT: hh:mm.ss" | datetime | | yes |
| total_num_reports | Total number of user reports received during a campaign. | integer | | no |

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
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
