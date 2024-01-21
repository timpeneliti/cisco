from flask import render_template, request, redirect
from app import app
from cisco_config import CiscoConfig

cisco_config = CiscoConfig()

def simplified_config(config):
    # Implement logika untuk menyederhanakan tampilan konfigurasi
    # Dalam contoh ini, kita akan menghapus baris-baris terkait SNMP
    # dan hanya menyertakan konfigurasi dari interface yang tidak dimatikan,
    # baris-baris IP route, baris-baris ACL, dan baris-baris NAT

    lines = config.split('\n')
    simplified_lines = []
    current_interface = None
    in_acl = False
    in_nat = False

    for line in lines:
        # Hilangkan baris-baris terkait SNMP
        if 'snmp-server' not in line.lower():
            # Identifikasi interface yang sedang diproses
            if line.lower().startswith('interface'):
                current_interface = line.strip()
                # Tambahkan baris interface ke hasil akhir
                simplified_lines.append(current_interface)
            elif current_interface and 'shutdown' in line.lower():
                # Hapus baris interface yang dimatikan (shutdown)
                current_interface = None
            elif current_interface is not None or line.lower().startswith(('ip route', 'access-list', 'ip nat')):
                # Tambahkan baris ke hasil akhir hanya jika sedang dalam interface yang tidak dimatikan,
                # atau baris-baris IP route, ACL, atau NAT
                simplified_lines.append(line)
                # Tentukan jika kita sedang di dalam konfigurasi ACL atau NAT
                in_acl = True if line.lower().startswith('access-list') else False
                in_nat = True if line.lower().startswith('ip nat') else False
            elif in_acl or in_nat:
                # Terus tambahkan baris dalam ACL atau NAT ke hasil akhir
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
