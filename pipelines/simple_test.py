from dagster import job, op, Definitions

@op
def hello_world():
    return "Hello, World!"

@op
def print_message(message):
    print(f"Message: {message}")
    return message

@job
def simple_pipeline():
    print_message(hello_world())

defs = Definitions(
    jobs=[simple_pipeline]
)