from flask import render_template, request, redirect
from app import app
from cisco_config import CiscoConfig

cisco_config = CiscoConfig()

@app.route('/')
def index():
    return render_template('index.html', devices=cisco_config.configurations)

@app.route('/save_config', methods=['POST'])
def save_config():
    device_name = request.form['device_name']
    config = request.form['config']
    cisco_config.save_config(device_name, config)
    return redirect('/')
