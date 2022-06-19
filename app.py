import os, logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, url_for, send_from_directory
from db import provide_db_services_c
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_INSTANCE_ID, Resource

exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ.get('traceConnectrionString')
)

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: "wso-service-repository-ui",
                SERVICE_NAMESPACE: "service-repository",
                SERVICE_INSTANCE_ID: "ui",
            }
        )
    )
)
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app, excluded_urls="client/.*/info,healthcheck")

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static\images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello')
def hello():
   tracer = trace.get_tracer(__name__)
   with tracer.start_as_current_span("Hello page render"):
      return render_template('hello.html', name = "Test, I am here!")

@app.route("/css/<path:path>")
def cssFileRoute(path):
   print(f'Request for css received { path }')
   return send_from_directory('static/sbs/css', path)

@app.route("/js/<path:path>")
def jsFileRoute(path):
   print(f'Request for js received { path }')
   return send_from_directory('static/sbs/js', path)

@app.route("/assets/<path:path>")
def assetsFileRoute(path):
   print(f'Request for assets received { path }')
   return send_from_directory('static/sbs/assets', path)

@app.route("/<path:path>")
def templateFileRoute(path):
   if os.path.exists(os.path.join('templates', path)):
      print('Request for templateFileRoute received')
      return render_template(path)
   else:
      return render_template('404.html'), 404


@provide_db_services_c
def countServices(c):
   items = list(c.query_items(
      query="SELECT VALUE COUNT(1) FROM c",
      enable_cross_partition_query=True
   ))
   return items[0]

if __name__ == '__main__':
   app.run()