FROM python:3.9
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir data
RUN mkdir downloads
ENTRYPOINT ["python3", "main.py"]
