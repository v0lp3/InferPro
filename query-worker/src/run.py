import json
import google.generativeai as genai

from pika import (
    PlainCredentials,
    BlockingConnection,
    ConnectionParameters,
    BasicProperties
)

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from definitions import INSTRUCTION, RABBITMQ_CREDENTIALS, GEMINI_TOKEN


genai.configure(api_key=GEMINI_TOKEN)


def query_gemini(ch: Channel, method: Basic.Deliver, _: BasicProperties, body: bytes):
    
    message = json.loads(body)
    response = model.generate_content(INSTRUCTION + "\n\n" + message["query"])

    message["response"] = response.text

model = genai.GenerativeModel('gemini-pro')
credentials = PlainCredentials(*RABBITMQ_CREDENTIALS)
parameters = ConnectionParameters(
    "rabbitmq",
    credentials=credentials,
    connection_attempts=5,
    retry_delay=15,
    heartbeat=600,
    blocked_connection_timeout=400,
)

cn = BlockingConnection(parameters)
ch = cn.channel(1337)

ch.basic_qos()

ch.queue_declare(
    queue="querying", durable=True, auto_delete=False
)

ch.basic_consume(
    queue="querying",
    on_message_callback=query_gemini,
)

ch.start_consuming()