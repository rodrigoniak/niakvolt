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
        


    def disconnect(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.serial.close()
            self.instrument = None
            self.port = None
            return
        raise RuntimeError("Cannot disconnect: device is already disconnected.")

    def turn_off(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.write_register(9, 0, functioncode=6)
            return
        raise RuntimeError("Device disconnected")

    def turn_on(self):
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.write_register(9, 1, functioncode=6)
            return
        raise RuntimeError("Device disconnected")
        
    def set_output_voltage(self, voltage):
        ensure_connected(self.instrument)
        v_set = int(float(voltage) * 100)
        self.instrument.write_register(0, v_set, functioncode=6)

    def set_max_amperage(self, amperage):
        ensure_connected(self.instrument)
        v_set = int(float(amperage) * 1000)
        self.instrument.write_register(1, v_set, functioncode=6)

def ensure_connected(instrument):
    if not (instrument and getattr(instrument, "serial", None) and instrument.serial.is_open):
        raise RuntimeError("Device disconnected")
        
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

@app.route("/api/off", methods=["GET"])
def api_off():
    try:
        source.turn_off()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/api/on", methods=["GET"])
def api_on():
    try:
        source.turn_on()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/api/set-output-voltage", methods=["POST"])
def api_set_output_voltage():
    voltage = request.json["voltage"]
    try:
        source.set_output_voltage(voltage)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/api/set-max-amperage", methods=["POST"])
def api_set_max_amperage():
    amperage = request.json["amperage"]
    try:
        source.set_max_amperage(amperage)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
