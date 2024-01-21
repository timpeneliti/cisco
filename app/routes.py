from flask import render_template, request, redirect
from app import app
from cisco_config import CiscoConfig

cisco_config = CiscoConfig()

def simplified_config(config):
    # Implement logika untuk menyederhanakan tampilan konfigurasi
    # Dalam contoh ini, kita akan menghapus baris-baris terkait SNMP,
    # line vty, dan blok line con, aux, vty
    # serta hanya menyertakan konfigurasi dari interface yang tidak dimatikan,
    # baris-baris IP route, baris-baris ACL, dan baris-baris NAT

    lines = iter(config.split('\n'))
    simplified_lines = []
    current_interface = None
    in_acl = False
    in_nat = False
    hostname_line_added = False  # Menandakan apakah baris hostname sudah ditambahkan

    for line in lines:
        # Hilangkan baris-baris terkait SNMP dan line vty
        if 'snmp-server' not in line.lower() and 'line vty' not in line.lower():
            # Hilangkan blok line con, aux, vty
            if line.lower().startswith(('line con', 'line aux', 'line vty')):
                while line.strip() != '!':
                    line = next(lines)
                continue

            # Identifikasi baris hostname dan tambahkan ke hasil akhir
            if line.lower().startswith('hostname'):
                simplified_lines.append(line)
                hostname_line_added = True
            # Identifikasi interface yang sedang diproses
            elif line.lower().startswith('interface'):
                current_interface = line.strip()
                # Tambahkan baris interface ke hasil akhir
                simplified_lines.append(current_interface)
            elif current_interface is not None and 'no ip address' in line.lower() and 'shutdown' in line.lower():
                # Tambahkan perintah no shutdown hanya jika interface memiliki no ip address dan shutdown
                simplified_lines.append(' no shutdown')
            elif current_interface is not None and 'shutdown' in line.lower():
                # Hapus baris interface yang dimatikan (shutdown)
                current_interface = None
            elif current_interface is not None or line.lower().startswith(('ip route', 'access-list', 'ip nat')):
                # Tambahkan baris ke hasil akhir hanya jika sedang dalam interface yang tidak dimatikan,
                # atau baris-baris IP route, ACL, atau NAT
                if line.lower().startswith('ip nat') and not in_nat:
                    # Jika ini adalah baris pertama dari konfigurasi NAT, tambahkan satu baris kosong
                    simplified_lines.append('!\n')
                    in_nat = True
                simplified_lines.append(line)
                # Tentukan jika kita sedang di dalam konfigurasi ACL atau NAT
                in_acl = True if line.lower().startswith('access-list') else False
            elif in_acl or in_nat:
                # Terus tambahkan baris dalam ACL atau NAT ke hasil akhir
                simplified_lines.append(line)

    # Jika baris hostname belum ditambahkan, tambahkan ke akhir
    if not hostname_line_added:
        simplified_lines.append('hostname <your_hostname_here>')  # Ganti dengan hostname yang sesuai

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
