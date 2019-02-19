FROM python:alpine3.9

WORKDIR /var/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /var/app
