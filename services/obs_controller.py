from obsws_python import ReqClient
class OBSController:

    def __init__(self, host="localhost", port=4455, password="Sg@273220"):
        self.host = host
        self.port = port
        self.password = password
        self.client = None

    def connect(self):
        self.client = ReqClient(host=self.host, port=self.port, password=self.password)

    def disconnect(self):
        if self.client:
            self.client.disconnect()

    def start_recording(self):
        self.client.start_record()

    def stop_recording(self):
        self.client.stop_record()