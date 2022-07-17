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
