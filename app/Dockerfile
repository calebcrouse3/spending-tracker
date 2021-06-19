FROM python:3.9
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY main.py app/main.py
ENTRYPOINT ["streamlit", "run", "app/main.py"]
