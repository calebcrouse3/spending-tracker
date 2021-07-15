FROM python:3.9
EXPOSE 8501
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:app:common:data_setup"
ENTRYPOINT ["streamlit", "run", "app/main.py"]
