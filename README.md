# iac-blueprint-builder
This component creates a IaC blueprint based on model instance representation from SODALITE KB. It is called and used by Xopera.

## swagger
It is accessible from http://154.48.185.202:8080/docs/ and needs the two following inputs:
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
## Prerequisites
All the requirements are stated in "requirements.txt".

## Docker 
Currently the container is accessible from:

```
docker pull mehrnooshaskarpour/iac-builder
```
