from ib_insync import IB

class IBConnection:
    _instance = None

    def __init__(self, host='127.0.0.1', port=7497, client_id=1):
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id

    def connect(self):
        if not self.ib.isConnected():
            self.ib.connect(self.host, self.port, clientId=self.client_id)

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = IBConnection()
            cls._instance.connect()
        return cls._instance.ib