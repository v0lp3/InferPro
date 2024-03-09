from os import environ

RABBITMQ_CREDENTIALS = (
    environ.get("RABBITMQ_USER", "user"),
    environ.get("RABBITMQ_PASSWORD"),
)

GEMINI_TOKEN = environ.get("GEMINI_TOKEN", "")

INSTRUCTION = "Replace the unsafe code to enhance security and produce valid code in C language. Returns only the modified function under markdown c code block:"
