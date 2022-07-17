from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_flask_exporter import PrometheusMetrics
from flask_opentracing import FlaskTracing
import logging
import os
from jaeger_client import Config
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
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

metrics = PrometheusMetrics(app)

mongo = PyMongo(app)

metrics.info('app_info', 'Application info', version='1.0.3')
record_requests_by_status = metrics.summary(
    'requests_by_status', 'Request latencies by status',
    labels={'status': lambda: request.status_code()}
)
record_page_visits = metrics.counter(
    'invocation_by_type', 'Number of invocations by type',
    labels={'item_type': lambda: request.view_args['type']}
)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


def init_tracer():
    logging.getLogger("").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name="backend",
        metrics_factory=PrometheusMetricsFactory(service_name_label="backend"),
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer = FlaskTracing(lambda: init_tracer(), True, app)

with tracer.tracer.start_span("backend-span") as span:
    span.set_tag("backend-tag", "100")


@app.route("/")
def homepage():
    return "Hello World", 200


@app.route("/api")
def my_api():
    answer = "something"
    return jsonify(response=answer)


@app.route("/star", methods=["POST"])
def add_star():
    star = mongo.db.stars
    name = request.json["name"]
    distance = request.json["distance"]
    star_id = star.insert({"name": name, "distance": distance})
    new_star = star.find_one({"_id": star_id})
    output = {"name": new_star["name"], "distance": new_star["distance"]}
    return jsonify({"result": output})


@app.route("/trace")
def trace():
    def remove_tags(text):
        tag = re.compile(r"<[^>]+>")
        return tag.sub("", text)

    with tracer.start_span("get-python-jobs") as span:
        res = requests.get("https://jobs.github.com/positions.json?description=python")
        span.log_kv({"event": "get jobs count", "count": len(res.json())})
        span.set_tag("jobs-count", len(res.json()))

        jobs_info = []
        for result in res.json():
            jobs = {}
            with tracer.start_span("request-site") as site_span:
                try:
                    jobs["description"] = remove_tags(result["description"])
                    jobs["company"] = result["company"]
                    jobs["company_url"] = result["company_url"]
                    jobs["created_at"] = result["created_at"]
                    jobs["how_to_apply"] = result["how_to_apply"]
                    jobs["location"] = result["location"]
                    jobs["title"] = result["title"]
                    jobs["type"] = result["type"]
                    jobs["url"] = result["url"]

                    jobs_info.append(jobs)
                    site_span.set_tag("http.status_code", res.status_code)
                    site_span.set_tag("company-site", result["company"])
                except Exception:
                    site_span.set_tag("http.status_code", res.status_code)
                    site_span.set_tag("company-site", result["company"])

    return jsonify(jobs_info)


@app.route("/error-400")
def create_400error():
    return "we created an error", 400


@app.route("/error")
def create_500error():
    return "we created an error", 500


if __name__ == "__main__":
    app.run(debug=False)
