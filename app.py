import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, url_for, send_from_directory

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static\images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route("/css/<path:path>")
def cssFileRoute(path):
   print(f'Request for css received { path }')
   return send_file('static/sbs/css/' + path)

@app.route("/js/<path:path>")
def jsFileRoute(path):
   print(f'Request for js received { path }')
   return send_file('static/sbs/js/' + path)

@app.route("/assets/<path:path>")
def assetsFileRoute(path):
   print(f'Request for assets received { path }')
   return send_file('static/sbs/assets/' + path)

@app.route("/<path:path>")
def templateFileRoute(path):
   print('Request for templateFileRoute received')
   return render_template(path)

if __name__ == '__main__':
   app.run()