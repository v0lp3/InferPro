import json
import git
import secrets
import os.path

from pika import (
    PlainCredentials,
    BlockingConnection,
    ConnectionParameters,
    BasicProperties
)

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from contextualizer import ContextParser
from infer import Infer, InferReport

from definitions import RABBITMQ_CREDENTIALS


def analyze(ch: Channel, method: Basic.Deliver, _: BasicProperties, body: bytes):
    
    message = json.loads(body)

    id = message["id"]
    entrypoint = message["entrypoint"]
    repository = message["repository"]

    download_path = os.path.join("/tmp", secrets.token_hex(16))

    git.Repo.clone_from(repository, to_path=download_path)

    vulnerabilities: list[InferReport] = Infer.run_analyzer(download_path, entrypoint)

    for vulnerability in vulnerabilities:
        prompt, code = ContextParser.get_prompt(vulnerability)

        data = {
            "id": id,
            "bug_type": vulnerability.bug_type,
            "qualifier": vulnerability.qualifier,
            "prompt": prompt,
            "code": code,
        }

        ch.basic_publish(
            exchange="",
            routing_key="querying",
            body=json.dumps(data),
            properties=BasicProperties(
                delivery_mode=2,
            ),
        )

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
    queue="analyzing", durable=True, auto_delete=False
)

ch.basic_consume(
    queue="analyzing",
    on_message_callback=analyze,
)

ch.start_consuming()