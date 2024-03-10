from os import environ

RABBITMQ_CREDENTIALS = (
    environ.get("RABBITMQ_USER", "user"),
    environ.get("RABBITMQ_PASSWORD"),
)

GEMINI_TOKEN = environ.get("GEMINI_TOKEN", "")

INSTRUCTION = """Main task: Replace the unsafe code to enhance security in C language.
Output: Return only the modified function under markdown c code block.
Notes:  
- The code should be valid and secure.
- The code should have minimal changes
- The code should have the same functionality as the original code
"""
