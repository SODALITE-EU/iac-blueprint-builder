# iac-blueprint-builder
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SODALITE-EU_iac-blueprint-builder&metric=alert_status)](https://sonarcloud.io/dashboard?id=SODALITE-EU_iac-blueprint-builder)

This component creates a TOSCA (IaC) blueprint based on a JSON model instance representation from SODALITE KB. It is called from the SODALITE IDE and registers the TOSCA CSAR blueprint with xopera-rest-api, to be later deployed by the user through the SDOALITE IDE. 

## swagger

If installed locally with docker it is accessible from http://localhost:8080/docs/ and needs the two following inputs:
“name” is an optional name as id for the returning token,
“data” is the content of the json file that should be copied.

The triggering command is:

```
curl --location --request POST 'localhost:8080/parse' \
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

*Note*: some tests require online services to be available (like the MODAK component) and are skipped by default.
Use `pytest --online` to include those tests in the test run.
Currently all of the online tests are also available as mocked tests (meaning they use pre-recorderd replies, for example to verify the parser).

## Docker

Currently the container is accessible from:

```
docker pull sodaliteh2020/iac-blueprint-builder
```
