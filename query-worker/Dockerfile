FROM python:slim


RUN pip install -q -U google-generativeai
RUN pip install pika

WORKDIR /query-worker

COPY . .

CMD ["python3", "/query-worker/src/run.py"]
