from os import environ

RABBITMQ_CREDENTIALS = (
    environ.get("RABBITMQ_USER", "user"),
    environ.get("RABBITMQ_PASSWORD"),
)
