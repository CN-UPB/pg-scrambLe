FROM python:3

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y install netcat && apt-get clean
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yml ./
COPY start.sh ./
COPY OsmSplitter.py ./
COPY Fetchfile.py ./
COPY Main_splitter.py ./
COPY OsmSchema.py ./
COPY OSMUtilityFunctions.py ./
COPY SonataSchema.py ./
COPY SonataSplitter.py ./
COPY SonataUtilityFunctions.py ./

COPY SonataNsd.json ./
COPY OsmNsd.json ./


RUN chmod +x ./start.sh

CMD watchmedo auto-restart --recursive --pattern="*.py" --directory="." /bin/bash start.sh
