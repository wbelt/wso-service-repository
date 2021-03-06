import os
import json
from flask import Flask, redirect, render_template, send_from_directory
from db import provide_redis

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_INSTANCE_ID, Resource

__version__ = "0.3"
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: "webui",
                SERVICE_NAMESPACE: "wso.core.service.repository",
                SERVICE_INSTANCE_ID: "main",
            }
        )
    )
)

mainTracer = trace.get_tracer(__name__)
traceExporter = AzureMonitorTraceExporter.from_connection_string(os.environ['wsoTraceConnectionString'])
span_processor = BatchSpanProcessor(traceExporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app, excluded_urls="hello")


@app.route('/')
def baseurl():
    return redirect('/index.html')


@app.route('/index.html')
def index():
    return render_template('index.html', list=rGetServices())


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello')
def hello():
    return render_template('hello.html')


@app.route('/test')
def test():
    return render_template('test.html', value=rCountServices())


@app.route("/css/<path:path>")
def cssFileRoute(path):
    return send_from_directory('static/sbs/css', path)


@app.route("/js/<path:path>")
def jsFileRoute(path):
    return send_from_directory('static/sbs/js', path)


@app.route("/assets/<path:path>")
def assetsFileRoute(path):
    return send_from_directory('static/sbs/assets', path)


@app.route("/<path:path>")
def genericTemplatePath(path):
    if os.path.exists(os.path.join('templates', path)):
        return render_template(path)
    else:
        span = trace.get_current_span()
        span.set_attribute("filename", path)
        span.add_event(f"Error 404: template file not found for { path }")
        return render_template('404.html'), 404


@mainTracer.start_as_current_span("redis: get all services")
@provide_redis
def rGetServices(r):
    return json.loads(r.get("wso.webui.service.table"))


@mainTracer.start_as_current_span("redis: count query")
@provide_redis
def rCountServices(r) -> int:
    return r.get("wso.webui.service.count")


if __name__ == '__main__':
    app.run()
