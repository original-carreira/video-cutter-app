from obswebsocket import obsws, requests


class OBSController:

    def __init__(self, host="localhost", port=4455, password="123456"):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None

    def connect(self):
        self.ws = obsws(self.host, self.port, self.password)
        self.ws.connect()

    def disconnect(self):
        if self.ws:
            self.ws.disconnect()

    def start_recording(self):
        self.ws.call(requests.StartRecording())

    def stop_recording(self):
        self.ws.call(requests.StopRecording())