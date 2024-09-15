## Dev Stack

* [Python 3.12](https://www.python.org/downloads/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [PyTest](https://docs.pytest.org/en/stable/)
* [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/)
* [Docker](https://www.docker.com/)

## Local Install

    python3.12 -m venv venv
    . venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    pytest app -v
    uvicorn app.main:app --port 8080

## Docker Install

    docker compose up

## Documentation

* [Swagger UI](http://localhost:8080/docs)
* [ReDoc](http://localhost:8080/redoc)

## Personal Notes

* Non-existing DMS responses are treated as empty lists.
* Default input dates are `yesterday` and `today`.
* Try the endpoint with wrong input dates for funny response messages. Enjoy it!
* Install `docker-compose-v2` instead `docker-compose-plugin`. There is a bug with the former plugin when upgrading to Ubuntu Noble.