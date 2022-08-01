from flask import Flask, render_template, request, redirect, url_for, jsonify  # For flask implementation
from jaeger_client import Config
from markupsafe import escape
from prometheus_client import metrics
from prometheus_flask_exporter import PrometheusMetrics
import logging
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
import requests
import re

import pymongo
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)


def init_tracer(backend):
    logging.getLogger("").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={"sampler": {"type": "const", "param": 1, }, "logging": True, },
        service_name=backend,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


# starter code
tracer = init_tracer("backend_service")

with tracer.start_span("first-span") as span:
    span.set_tag("first-tag", "100")

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')
record_requests_by_status = metrics.summary(
    'requests_by_status', 'Request latencies by status',
    labels={'status': lambda: request.status_code()}
)
record_page_visits = metrics.counter(
    'invocation_by_type', 'Number of invocations by type',
    labels={'item_type': lambda: request.view_args['type']}
)


@app.route("/")
def homepage():
    message = "Hello Gorgeous"
    with tracer.start_span("home_route") as span2:
        span2.set_tag("message", message)
        span2.log_kv({'event': 'test message', 'life': 42})
    return message


@app.route("/api")
def my_api():
    answer = "something in this backend api"
    with tracer.start_span("api") as span3:
        span3.set_tag("api_route_span", answer)
        span3.log_kv({'event': 'in /api route'})
    return jsonify(response=answer)


@app.route("/star", methods=["POST"])
def add_star():
    with tracer.start_span("add_star_api") as span4:
        span4.set_tag("post_star_span", "star posted")
        span4.log_kv({'event': 'in add star route'})
        try:
            name = request.json["name"]
            distance = request.json["distance"]
            new_star = request.json["name+****"]
            new_distance = len(distance)
            output = {"name": new_star, "distance": new_distance}
            span4.set_tag("http.status_code", output.status_code)
            span4.set_tag("try failed", "output")
        except Exception:
            span4.set_tag("http.status_code", output.status_code)
            span4.set_tag("try exception", "output")
    return jsonify(output)


@app.route("/error-400")
def create_400error():
    with tracer.start_span("error_400") as span5:
        span5.set_tag("error", "400 error encountered")
        span5.log_kv({'event': 'in error route'})
    return "we created a 400 error", 400


@app.route("/error")
def create_500error():
    return "we created a 500 error", 500


if __name__ == "__main__":
    app.run(debug=False)
