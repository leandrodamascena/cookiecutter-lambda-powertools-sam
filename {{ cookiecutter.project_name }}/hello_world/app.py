import random
from time import gmtime, strftime
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
{%- if cookiecutter["Powertools Logging"] == "enabled"%}
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
{%- endif %}
{%- if cookiecutter["Powertools X-Ray Tracing"] == "enabled"%}
from aws_lambda_powertools import Tracer
{%- endif %}
{%- if cookiecutter["Powertools Metrics"] == "enabled"%}
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
{%- endif %}

app = APIGatewayRestResolver()
{%- if cookiecutter["Powertools X-Ray Tracing"] == "enabled"%}
tracer = Tracer()
{%- endif %}
{%- if cookiecutter["Powertools Logging"] == "enabled"%}
logger = Logger()
{%- endif %}
{%- if cookiecutter["Powertools Metrics"] == "enabled"%}
metrics = Metrics()
{%- endif %}

@app.get("/hello")
{%- if cookiecutter["Powertools X-Ray Tracing"] == "enabled"%}
@tracer.capture_method
{%- endif %}
def hello():

    random_number = random.randint(1,4)

    {%- if cookiecutter["Powertools Metrics"] == "enabled" %}
    # adding custom metrics
    metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)

    {%- endif %}

    {%- if cookiecutter["Powertools X-Ray Tracing"] == "enabled" %}

    # adding subgements, annotations and metadata
    with tracer.provider.in_subsegment("## random_number") as subsegment:
        subsegment.put_annotation(key="RandomNumber", value=random_number)
        subsegment.put_metadata(key="date", value=strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    {%- endif %}

    # Emulating an HTTP code response based on a random number.
    if random_number < 9:
        {%- if cookiecutter["Powertools Logging"] == "enabled" %}
        # structured log
        logger.info("INFO LOG - hello world API - HTTP 200")
        {%- endif %}
        return {"status": "healthy"}, 200
    else:
        {%- if cookiecutter["Powertools Logging"] == "enabled"%}
        # structured log
        logger.error("ERROR LOG - hello world API - HTTP 500")
        {%- endif %}
        return {"status": "unhealthy"}, 500

# lambda_handler
{%- if cookiecutter["Powertools Logging"] == "enabled" %}
# Logging Lambda invocation
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
{%- endif %}
{%- if cookiecutter["Powertools X-Ray Tracing"] == "enabled" %}
# Adding tracer
@tracer.capture_lambda_handler
{%- endif %}
{%- if cookiecutter["Powertools Metrics"] == "enabled" %}
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
{%- endif %}
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
