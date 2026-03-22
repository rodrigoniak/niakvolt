from flask import Flask, jsonify, render_template, request
import minimalmodbus
import serial.tools.list_ports

app = Flask(__name__)

class Source:
    def status(self):
        return "DISCONNECTED"
        
    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]
        
    def connect(self, port):
        instrument = minimalmodbus.Instrument(port, 1)
        instrument.serial.baudrate = 9600
        instrument.serial.bytesize = 8
        instrument.serial.timeout = 0.5
        instrument.mode = minimalmodbus.MODE_RTU
        
        v_set = int(2.5 * 100)
        instrument.write_register(0, v_set, functioncode=6) 
        print(port)

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

@app.route("/api/connect", methods=["POST"])
def api_connect():
    port = request.json["port"]

    try:
        source.connect(port)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
