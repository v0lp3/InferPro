import json
import secrets
import jwt
import shutil
import logging
import os.path

from time import time

from flask import Flask, request, render_template, make_response, send_file

from pika import (
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)

from pika.spec import BasicProperties

from definitions import RABBITMQ_CREDENTIALS, FLASK_SECRET_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s",
)

app = Flask(__name__, static_folder="../static", template_folder="../templates")

credentials = PlainCredentials(*RABBITMQ_CREDENTIALS)
parameters = ConnectionParameters(
    "rabbitmq",
    credentials=credentials,
    connection_attempts=5,
    retry_delay=15,
    heartbeat=600,
    blocked_connection_timeout=400,
)


def get_ids():
    token = request.cookies.get("token")

    try:
        decoded_token = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return decoded_token["ids"]
    except:
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    request_data = request.form.to_dict()

    try:
        entrypoint = request_data.get("entrypoint", "main.c")
        repository = request_data["repository"]
    except:
        return "Invalid request", 400

    id = secrets.token_hex(32)

    data = {  # request can contain more data than needed
        "entrypoint": entrypoint,
        "repository": repository,
        "id": id,
    }

    ids = get_ids() + [id]

    token = jwt.encode({"ids": ids}, app.secret_key, algorithm="HS256")

    resp = make_response("Done", 200)
    resp.set_cookie("token", token)

    ch.basic_publish(
        exchange="",
        routing_key="analyzing",
        body=json.dumps(data),
        properties=BasicProperties(
            delivery_mode=2,
        ),
    )

    return resp


@app.route("/patchs", methods=["GET", "POST"])
def view():
    ids = get_ids()

    if request.method == "GET":
        return render_template("patchs.html", patchs=ids)
    else:
        id = request.form.get("id")

        if id not in ids:
            return "Invalid request", 400

        patchs_path = os.path.join("/storage", id, "patchs")

        timestamp = int(time())
        output_file = os.path.join("/tmp", f"patchs_{id}_{timestamp}")

        try:
            shutil.make_archive(output_file, "zip", patchs_path)
            return send_file(f"{output_file}.zip", as_attachment=True)
        except Exception as e:
            logging.info(e)
            return "Error", 500


cn = BlockingConnection(parameters)
ch = cn.channel(1337)

ch.basic_qos()

if not FLASK_SECRET_KEY:
    app.secret_key = secrets.token_hex(32)
else:
    app.secret_key = FLASK_SECRET_KEY

app.run(host="0.0.0.0", port=5000)
