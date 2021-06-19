FROM python:3.9
EXPOSE 8501
WORKDIR /src
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir ./data
RUN mkdir ./app
COPY main.py ./app/main.py
ENTRYPOINT ["streamlit", "run", "./app/main.py"]
