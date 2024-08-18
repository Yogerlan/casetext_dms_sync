## Dev Stack

* [Python 3.12](https://www.python.org/downloads/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [pytest](https://docs.pytest.org/en/stable/)
* [Docker](https://www.docker.com/)

## Local Install

    python3.12 -m venv venv
    . venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    pytest app
    uvicorn app.main:app --port 8080

## Docker Install

    docker-compose up web

## Documentation

* [Swagger UI](http://localhost:8080/docs)
* [ReDoc](http://localhost:8080/redoc)

## Personal Notes