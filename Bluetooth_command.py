import serial
import time

MIN_SEND_INTERVAL = 0.15


class BluetoothCommandr:
    def __init__(self, port="COM4", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.bt = None
        self.last_message = None
        self.last_send_time = 0

    def connect(self):
        try:
            self.bt = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1
            )

            time.sleep(2)

            print(f"Bluetooth conectado en {self.port}")
            return True

        except Exception as e:
            print(f"Error conectando Bluetooth: {e}")
            self.bt = None
            return False

    def send_speed(self, speed):
        if self.bt is None:
            print("Bluetooth no conectado")
            return False

        try:
            speed = int(speed)

            if not 0 <= speed <= 255:
                print("La velocidad debe estar entre 0 y 255")
                return False

            message = f"V-{speed}\n"
            self.bt.write(message.encode("utf-8"))

            self.last_message = None
            self.last_send_time = time.time()

            print(f"Velocidad enviada: {speed}")
            return True

        except (TypeError, ValueError):
            print("El valor de velocidad no es válido")
            return False

        except serial.SerialException as e:
            print(f"Error enviando velocidad: {e}")
            return False

    def send_navigation_data(self, nav_data):
        if self.bt is None:
            return

        action = nav_data["action"]

        if action == "NAVIGATE":
            now = time.time()

            if now - self.last_send_time < MIN_SEND_INTERVAL:
                return

            angle = nav_data["angle"]
            distance = nav_data["distance"]

            message = f"F-{angle:.1f},{distance:.1f}\n"

        elif action == "STOP":
            message = "S\n"

        else:
            return  # HOLD no envía nada

        if message == self.last_message:
            return

        try:
            self.bt.write(message.encode("utf-8"))

            self.last_message = message
            self.last_send_time = time.time()

            print(f"Enviado: {message.strip()}")

        except serial.SerialException as e:
            print(f"Error enviando comando: {e}")

    def close(self):
        if self.bt is not None:
            try:
                self.bt.write(b"S\n")
                time.sleep(0.1)
                self.bt.close()

            except serial.SerialException as e:
                print(f"Error cerrando Bluetooth: {e}")

            finally:
                self.bt = None
                self.last_message = None
                print("Bluetooth cerrado")
