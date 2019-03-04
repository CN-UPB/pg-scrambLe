FROM python:3

RUN apt-get update && apt-get -y install netcat && apt-get clean
RUN sudo apt update && add-apt-repository -y "deb [arch=amd64]
 http://osm-download.etsi.org/repository/osm/debian/ReleaseFIVE stable IM osmclient devops"
RUN sudo apt update
RUN sudo apt install python-osm-im

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

RUN chmod +x ./start.sh

CMD ["./start.sh"]
