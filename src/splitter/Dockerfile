FROM python:3

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y install netcat && apt-get clean
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yml ./
COPY start.sh ./
COPY OSM/OsmSplitter.py ./
COPY Fetchfile.py ./
COPY Main_splitter.py ./
COPY OSM/OsmSchema.py ./
COPY OSM/OSMUtilityFunctions.py ./
COPY Sonata/SonataSchema.py ./
COPY Sonata/SonataSplitter.py ./
COPY Sonata/SonataUtilityFunctions.py ./


RUN chmod +x ./start.sh

CMD watchmedo auto-restart --recursive --pattern="*.py" --directory="." /bin/bash start.sh
