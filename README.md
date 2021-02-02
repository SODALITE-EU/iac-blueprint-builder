# iac-blueprint-builder
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SODALITE-EU_iac-blueprint-builder&metric=alert_status)](https://sonarcloud.io/dashboard?id=SODALITE-EU_iac-blueprint-builder)

This component creates a IaC blueprint based on model instance representation from SODALITE KB. It is called and used by xopera.

## swagger

It is accessible from http://154.48.185.202:8080/docs/ (for the purpose of release one, everything was running on 154.48.185.202) and needs the two following inputs:
“name” is an optional name as id for the returning token,
“data” is the content of the json file that should be copied.

The triggering command is:

```
curl --location --request POST '154.48.185.202:8080/parse' \
--header 'Content-Type: application/json' \
--data-raw '{
	"name" : "test2",
	"data" : {...}
}'
```
An example of the proper input is in "test/fixture.json".

## Prerequisites

All the requirements are stated in "requirements.txt".

## Test

1. Install local modules
   `pip3 install -e .`
2. Run tests
   `pytest`

## Docker

Currently the container is accessible from:

```
docker pull mehrnooshaskarpour/iac-builder
```
