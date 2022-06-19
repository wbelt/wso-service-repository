import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, url_for, send_from_directory
from db import provide_db_services_c

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static\images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello')
def hello():
   print('Request for hello page received')
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