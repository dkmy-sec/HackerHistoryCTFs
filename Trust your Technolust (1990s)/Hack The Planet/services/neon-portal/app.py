from flask import Flask, request, jsonify
import hmac, hashlib, time, os
APP_KEY = os.getenv("API_HMAC_KEY", "changeme")
app = Flask(__name__)
@app.get('/api/list')
def list_nodes():
    node = request.args.get('node', '/')
    ts   = request.args.get('ts', '0')
    sig  = request.args.get('sig', '')
    try:
        ts_i = int(ts)
    except:
        return ("bad ts", 400)
    if abs(time.time() - ts_i) > 90:
        return ("time skew", 401)
    mac = hmac.new(APP_KEY.encode(), f"{node}:{ts}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, sig):
        return ("bad sig", 401)
    return jsonify({"node": node, "children": ["garbage","finance","hr"]})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
