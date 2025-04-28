from flask import Flask, request, render_template_string, redirect
import subprocess

app = Flask(__name__)

WPA_SUPPLICANT_CONF = '/etc/wpa_supplicant/wpa_supplicant.conf'

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
<title>WiFi Setup</title>
<style>
body { font-family: sans-serif; padding: 2em; }
input { margin: 0.5em 0; padding: 0.5em; width: 90%%; }
button { padding: 0.5em 1em; }
</style>
</head>
<body>
<h2>Connect to WiFi</h2>
<form method="POST">
    <input type="text" name="ssid" placeholder="WiFi SSID" required><br>
    <input type="password" name="password" placeholder="WiFi Password" required><br>
    <button type="submit">Connect</button>
</form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def wifi_setup():
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form['password']
        add_network(ssid, password)
        restart_wifi_manager()
        return redirect('/')
    return render_template_string(HTML_FORM)

def add_network(ssid, password):
    network_block = f'''
network={{
    ssid="{ssid}"
    psk="{password}"
}}
'''
    with open(WPA_SUPPLICANT_CONF, 'a') as f:
        f.write(network_block)

def restart_wifi_manager():
    subprocess.run(["sudo", "systemctl", "restart", "wifi-manager.service"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
