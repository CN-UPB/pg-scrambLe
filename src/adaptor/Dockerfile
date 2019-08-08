FROM python:3.6

RUN apt-get update && apt-get -y install netcat && apt-get clean

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yml ./
COPY start.sh ./
COPY adaptor.py ./
COPY tests ./tests
COPY wrappers ./wrappers

RUN chmod +x ./start.sh

CMD ["./start.sh"]