FROM python:3

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y install netcat && apt-get clean
RUN apt-get install software-properties-common -y
RUN apt-get install apt-transport-https ca-certificates -y
RUN curl https://osm-download.etsi.org/repository/osm/debian/ReleaseFIVE/OSM%20ETSI%20Release%20Key.gpg | apt-key add -
RUN add-apt-repository -y "deb [arch=amd64] https://osm-download.etsi.org/repository/osm/debian/ReleaseFIVE stable IM osmclient devops"
RUN apt update -y
RUN apt install python-osm-im -y

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yml ./
COPY start.sh ./
COPY translator.py ./
COPY utilities.py ./
COPY descriptorReader.py ./
COPY descriptorWriter.py ./


COPY hackfest_multivdu_nsd.yaml ./
COPY sonata-demo.yml ./

COPY nsd-schema.yml ./
COPY vnfd-schema.yml ./

RUN chmod +x ./start.sh

CMD ["./start.sh"]
