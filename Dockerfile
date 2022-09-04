FROM python:3.10.0

WORKDIR .

RUN apt-get update && apt-get install -y git
COPY requirements.txt requirements.txt
RUN python3.10 -m pip install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]
