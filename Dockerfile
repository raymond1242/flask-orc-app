FROM ubuntu:18.04

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    python3-pip \
    python3-dev \
    # build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    # postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# copy project
COPY . .

ENTRYPOINT ["python3"]
CMD ["app.py"]
