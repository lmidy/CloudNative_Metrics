import os
import requests
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

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


def get_counter(counter_endpoint):
    counter_response = requests.get(counter_endpoint)
    return counter_response.text


def increase_counter(counter_endpoint):
    counter_response = requests.post(counter_endpoint)
    return counter_response.text


@app.route("/visit")
def visit():
    counter_service = os.environ.get('COUNTER_ENDPOINT', default="http://localhost:8081")
    counter_endpoint = f'{counter_service}/api/counter'
    counter = get_counter(counter_endpoint)
    increase_counter(counter_endpoint)

    return f" You're visitor number {counter} in here! \n\n"


@app.route("/")
def homepage():
    return render_template("main.html")


@app.route("/error-400")
def create_400error():
    return "we created an error", 400


@app.route("/error")
def create_500error():
    return "we created an error", 500


if __name__ == "__main__":
    app.run()
