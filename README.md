# INSPIRE-Next


## About

INSPIRE is the leading information platform for High Energy Physics (HEP) literature.
It provides users with high quality, curated metadata covering the entire corpus of
HEP and the fulltext of all such articles that are Open Access.

This repository contains the source code of the next version of INSPIRE, which is
slowly being deprecated.
It is based on version 3 of the [`Invenio Digital Library Framework`](http://inveniosoftware.org/).

A preliminary version of the documentation is available on [`Read the Docs`](https://inspirehep.readthedocs.io/en/latest/).


# Running tests
1. only needs to be run once, or when the dependencies change
```shell
docker compose -f services.yml build --force-rm base
```
2. Spin up `next`
```shell 
docker compose -f docker-compose.test.yml up test-database test-indexer test-rabbitmq test-redis test-web test-worker
```
3. On the `worker`  container run `scripts/clear_pycache` (optional)
4. On the `worker`  container run `pytest ...`

``` shell
pytest tests/integration/workflows # workflows
pytest tests/integration --ignore tests/integration/workflows # sync integration tests
pytest tests/integration_async # async integration tests
pytest tests/unit # unit tests
```


