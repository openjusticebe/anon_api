## Anonimization testing api
Simple api to submit text to a selec choice of depersonalization algorithms, and get results back.

### Usage
Deployment is through docker or pipenv

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# pipenv
> make install
> make serve-dev
```

Then check these local URI's:

* http://127.0.0.1:5000 for root
* http://127.0.0.1:5000/docs for OpenAPI documentation
