from flask import render_template, request, redirect
from app import app
from cisco_config import CiscoConfig

cisco_config = CiscoConfig()

def simplified_config(config):
    # Implement logika untuk menyederhanakan tampilan konfigurasi
    # Dalam contoh ini, kita akan menghapus baris-baris terkait SNMP

    lines = config.split('\n')
    simplified_lines = []

    for line in lines:
        # Hilangkan baris-baris terkait SNMP
        if 'snmp-server' not in line.lower():
            simplified_lines.append(line)

    return '\n'.join(simplified_lines)

@app.route('/')
def index():
    return render_template('index.html', devices=cisco_config.configurations, simplified_config=simplified_config)

@app.route('/save_config', methods=['POST'])
def save_config():
    device_name = request.form['device_name']
    config = request.form['config']
    cisco_config.save_config(device_name, config)
    return redirect('/')
