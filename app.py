from flask import Flask, jsonify, render_template, request
import minimalmodbus
import threading
import serial.tools.list_ports

app = Flask(__name__)

class Source:
    def __init__(self):
        self.instrument = None
        self.lock = threading.Lock()
        self.port = None

    def status(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            s = self.instrument.read_register(9, functioncode=3)
            if s == 1:
                return "ON"
            else:
                return "OFF"
        return "DISCONNECTED"
        
    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]
        
    def connect(self, port):
        self.port = port
        self.instrument = minimalmodbus.Instrument(port, 1)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.timeout = 0.5
        self.instrument.mode = minimalmodbus.MODE_RTU
        
        v_set = int(2.5 * 100)
        self.instrument.write_register(0, v_set, functioncode=6)
        
        
    def disconnect(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.serial.close()
            self.instrument = None
            self.port = None
            return
        raise RuntimeError("Cannot disconnect: device is already disconnected.")
        
    def poweroff(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.write_register(9, 0, functioncode=6)
            return
        raise RuntimeError("Cannot disconnect: device is already disconnected.")

source = Source()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(status=source.status(), port=source.port)

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
     
@app.route("/api/disconnect", methods=["GET"])
def api_disconnect():
    try:
        source.disconnect()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/api/poweroff", methods=["GET"])
def api_off():
    try:
        source.poweroff()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
