from flask import Flask, jsonify, render_template, request
import serial.tools.list_ports

app = Flask(__name__)

class Source:
    def status(self):
        return "DISCONNECTED"
    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

source = Source()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(status=source.status())

@app.route("/api/ports")
def api_ports():
    return jsonify(source.list_ports())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
