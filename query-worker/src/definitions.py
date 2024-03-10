from os import environ

RABBITMQ_CREDENTIALS = (
    environ.get("RABBITMQ_USER", "user"),
    environ.get("RABBITMQ_PASSWORD"),
)

GEMINI_TOKEN = environ.get("GEMINI_TOKEN")

INSTRUCTION = """Main Task: Replace the unsafe code C code function to improve its security.

Output: Return only the modified function as a code block formatted in markdown for C code.

Notes:

- The modified function must be valid C code.
- Minimize changes to the original code.
- The modified function should maintain the same functionality as the original.
- Do not modify the function signature (name and arguments).
"""
