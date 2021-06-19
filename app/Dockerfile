FROM python:3.9
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY main.py app/main.py
EXPOSE 80
ENTRYPOINT ["streamlit", "run", "app/main.py"]
