from flask import Flask, request, jsonify
app = Flask(__name__)
app.secret_key = 'anm'
import subprocess


def exec_get_op(exe):
    print ("Command to run:", exe)
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break


def get_console(command):
    lines = list()
    for line in exec_get_op('{}'.format(command)):
        if line.strip():
            lines.append(line.strip())
    return lines

#192.168.185.52:5000/listIP
@app.route('/listIP')
def listIP():
    op = get_console('sudo iptables -S')
    return jsonify({'output': op}), 200


# http://192.168.185.52:5000/addIP?ip=<ipaddress_to_block>
# iptables -A INPUT -s IP-ADDRESS -j DROP
@app.route('/addIP')
def addIP():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({'error': 'Could not find ip. URL format removeBlockedIP?ip=<ipaddress_to_block>'}), 500
    op = get_console('iptables -A INPUT -s {} -j DROP'.format(ip))
    return jsonify({'output': op}), 200




# http://192.168.185.52:5000/removeBlockedIP?ip=<ipaddress_to_unblock>
# iptables -D INPUT -s IP-ADDRESS -j DROP
@app.route('/removeBlockedIP')
def removeBlockedIP():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({'error': 'Could not find ip. URL format removeBlockedIP?ip=<ipaddress_to_unblock>'}), 500
    op = get_console('iptables -D INPUT -s {} -j DROP'.format(ip))
    return jsonify({'output': op}), 200


# curl -d filter="--ip.proto=TCP --if=d03" -d tag="out-tcp" -X POST http://192.168.185.71:5000/listInstance
# iptables -A INPUT -s IP-ADDRESS -j DROP
@app.route('/addInstance', methods=['POST'])
def addInstance():
    filter = request.form.get('filter')
    tag = request.form.get('tag')
    if not filter or not tag:
        return jsonify({'error': 'Could not find ip. URL format -  /addInstance?filter=<filter_string>&tag=<tag>'}), 500
    command = 'sudo bitrate -i ens4 01::71 01::72 {} --format=influx --influx-user="admin" --influx-pwd="admin" --influx-tag="{}" --influx-url="http://localhost:8086/write?db=anm" >/dev/null 2>&1 &'.format(filter, tag)
    op = get_console(command)
    return jsonify({'output': op}), 200


# 192.168.185.52:5000/killInstance?id=<id-seen in listInstance output>
@app.route('/killInstance')
def killInstance():
    id = request.args.get('id')
    if not id:
        return jsonify({'error': 'Could not find id. URL format - /killInstance?id=<id-seen in listInstance output>'}), 500
    op = get_console('sudo kill -9 {}'.format(id))
    return jsonify({'output': op}), 200


#192.168.185.52:5000/listInstance
@app.route('/listInstance')
def listInstance():
    op = get_console('ps -lef | grep bitrate')
    return jsonify({'output': op}), 200


if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0')