# Upload API
Upload API offers stateless (ie: no storage or recording of data) operations (Text extraction, pseudonymisation, OCR, ...) to the upload interface from the OpenJustice platform.

If offers a Rest API, documented via OpenAPI, and integrations with more specific functions (Apache Tika, Pyghotess, ...)

This API can already:
- pseudonymise a text
- extract metadata from a pdf file
- OCR process a file in multiple ways

Those functionalities already cover all this component should do, any future work looks to improve what's already offered.

## Installation
Clone the repository to your directory of choice:
```bash
> git clone https://github.com/openjusticebe/anon_api.git
> cd anon_api
```

Once in the root directory, you can run the API with docker (for testing) or using poetry (for development).

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# poetry
> poetry install
```

### Poetry installation
Poetry installs a local, isolated python environment, to avoid conflicts with your system's python modules. See [here](https://python-poetry.org/docs/).

A recent [python](https://www.python.org/downloads/) version (>=3.7) will also be needed.

## Usage
```bash
# Run locally in debug mode
> poetry run api --debug

```

These local URI's provide interaction and documentation for the endpoint

* http://127.0.0.1:5005 for root
* http://127.0.0.1:5005/docs for OpenAPI documentation

### Configuration:
See `config_default.toml` file to create a local `config.toml` file for the API to use.
Configuration can also happen through environmen variables, see `main.py` for a list.

```bash
# Run locally in debug mode with a config file.
> poetry run api --config config.toml --debug
```

## Roadmap
1. Provide full support for the OpenJustice upload interactions


## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.fr.html)

## Legacy
This API has been built up from a previous incarnation, as such some legacy code is still present, such as testing multiple anonymisation algorithms. See below for info
### Configuration
Algorithms are detailed in the `config_default.yaml` file for the moment.
Parameters are not supported yet. A check is done on the required environment variables to know if the
algorithm is available.

A specific module also has to be added to the `anon_api/modules` folder, which is responsible for querying and applying the results from the selected algorithm.

### Testing
This component uses BDD (behave). To run it (a local tika server is needed):
```bash
poetry run python -m behave tests/behave
```
