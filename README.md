# Flask OCR API

### Requirements

- Python 3.9+
- Tesseract 4.0+
- Docker & Docker Compose

### Set the virtual env

```console
$ python -m venv venv
```

## Installation

#### Install requirements

```console
$ make install
```

#### Build docker images

```console
$ make build
```

#### Start services

```console
$ make start
```

#### Create database

```console
$ make database
```

Now, you should be able to go [localhost:5000/](localhost:5000/)  to see the app running.

---

### Stop services

```console
$ make stop
```

### Postman requests

You can import the postman collection from this [link](https://lunar-equinox-903112.postman.co/workspace/level-up~a906f4ea-a3f0-4e44-8de2-d6fba3329401/collection/4751661-94d0797a-5dcf-45b8-a09a-1245e5b6a795?action=share&creator=4751661) to test the API.

Don't forget to change the `base_url` variable to your local url, by default is `localhost:5000/`. Also, fill out the body params and select a file to upload in the `upload_image` request.
