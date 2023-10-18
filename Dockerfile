FROM ubuntu:latest

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get install -y libtesseract-dev \
    && apt-get install -y python3 python3-pip \
    && apt install -y libsm6 libxext6

RUN apt-get install -y python3-distutils python3-pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["app.py"]
