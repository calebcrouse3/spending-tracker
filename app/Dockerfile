FROM python:3.9
EXPOSE 8501
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir app
RUN mkdir data
ENTRYPOINT ["streamlit", "run", "app/main.py"]
