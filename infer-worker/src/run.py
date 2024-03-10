import json
import git
import secrets
import os.path
import os
import logging


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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s",
)


def analyze(ch: Channel, method: Basic.Deliver, _: BasicProperties, body: bytes):
    
    message = json.loads(body)

    logging.info(f"Received message: {message}")

    id = secrets.token_hex(16)
    entrypoint = message["entrypoint"]
    repository = message["repository"]

    id_path = os.path.join(
        "/tmp",
        "storage",
        id,
    )
    download_path = os.path.join(id_path, "repository")

    os.makedirs(download_path, exist_ok=True)

    git.Repo.clone_from(repository, to_path=download_path)

    vulnerabilities: list[InferReport] = Infer.run_analyzer(download_path, entrypoint)

    unique_procedures = set(
        map(lambda vuln: (vuln.source_path, vuln.procedure_line), vulnerabilities)
    )

    for procedure in unique_procedures:
        source_path, procedure_line = procedure

        inherent_vulnerabilities = sorted(
            list(
                filter(
                    lambda vuln: vuln.source_path == source_path
                    and vuln.procedure_line == procedure_line,
                    vulnerabilities,
                )
            ),
            key=lambda vuln: vuln.line,
            reverse=True,
        )

        vulnerabilities = list(
            filter(lambda vuln: vuln not in inherent_vulnerabilities, vulnerabilities)
        )

        prompt = ContextParser.get_prompt(inherent_vulnerabilities)

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
        
    ch.basic_ack(delivery_tag=method.delivery_tag)


def create_patch(ch: Channel, method: Basic.Deliver, _: BasicProperties, body: bytes):
    message = json.loads(body)

    logging.info(f"Received message: {message}")

    id = message["id"]
    source_path = message["source_path"]
    procedure_line = message["procedure_line"]
    response = message["response"]

    patch = ContextParser.get_patch(source_path, procedure_line, response)

    filename = source_path.split("/")[-1]

    patch_dir = os.path.join("/tmp", "storage", id, "patch")

    os.makedirs(patch_dir, exist_ok=True)

    patches_path = os.path.join(patch_dir, f"{filename}_{procedure_line}.patch")

    with open(patches_path, "w") as f:
        f.write(patch)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


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