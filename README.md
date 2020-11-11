## Anonimization testing api
Simple api to submit text to a selec choice of depersonalization algorithms, and get results back.

It has two main interfaces:
 - Rest API, documented via OpenAPI, for running the selected algorithms
 - GraphQL API, to list the algorithms, their availibility and parameters

### Configuration
Algorithms are detailed in the `config_default.yaml` file for the moment.
Parameters are not supported yet. A check is done on the required environment variables to know if the
algorithm is available.

A specific module also has to be added to the `anon_api/modules` folder, which is responsible for querying and applying the results from the selected algorithm.

### Usage
Deployment is through docker or pipenv

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# poetry
> poetry install
> poetry run api
```

Then check these local URI's:

* http://127.0.0.1:5000 for root
* http://127.0.0.1:5000/docs for OpenAPI documentation
* http://127.0.0.1:5000/gql for GraphQL interface

Example curl command to test graphql interface:
```bash
curl -X POST -H "Content-Type: application/json" --data '{ "query": "{ algorithms {id, description}}"}' https://anon-api.openjustice.be/gql/
```
