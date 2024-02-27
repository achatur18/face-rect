# FaceRect

FaceRect is a facial recognition usecase.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```
## Setup

Start mongodb server using docker.

```bash
docker run -p 27017:27017 mongo
```

For using mongo vector search. You might have to create db and index on atlas and provide URL, dbname etc details in config.toml file.

Start uvicorn server.

```bash
uvicorn main:app --reload
```

Server will be running on:

```bash
localhost:8000/docs
```
