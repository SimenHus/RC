import asyncio

from bleak import BleakClient
from PySide6.QtCore import QThread, Signal, Slot


# Hentet fra Schimen sim kode
COMMAND_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
COMMAND_WRITE_UUID  = "12345678-1234-5678-1234-56789abcdef1"

ERROR_COMMAND             = 0
ACK_COMMAND               = 1
PING_COMMAND              = 2
LEFT_MOTOR_COMMAND        = 3
RIGHT_MOTOR_COMMAND       = 4
WEAPON_MOTOR_COMMAND      = 5
DEFAULT_INTERFACE_COMMAND = 6

ERROR_UNRECOGNIZED = 0
ERROR_TIMEOUT      = 1
ERROR_PARSE        = 2
ERROR_VALUE        = 3

COMMAND_START = b'%'
COMMAND_END = b'&'



# https://stackoverflow.com/questions/59645272/how-do-i-pass-an-async-function-to-a-thread-target-in-python
# https://stackoverflow.com/questions/63858511/using-threads-in-combination-with-asyncio
# https://bleak.readthedocs.io/en/latest/usage.html

class Client(QThread):
    dataSignal = Signal(list)
    statusSignal = Signal(str)

    def __init__(self, host='24:71:89:cc:09:05', port=4, *args, **kwargs):
        """
        host: str - Host MAC address to connect to
        port: int - Port to connect to
        """
        super().__init__(*args, **kwargs)

        self.outgoingQueue = asyncio.Queue()

        # Server variables
        self.HOST = host
        self.PORT = port

        # Threading variables
        self.running = True
        self.daemon = True

    def BLENotificationCB(self, _, data) -> None:
        """
        Bluetooth callback function. Handles incoming data
        """
        if len(data) != 2:
            print(f'Received strange notification {data}')
            return
        
        head, value = data
        key = (0xE0 & head) >> 5
        address = 0x07 & head
        self.dataSignal.emit((key, address, value))


    @Slot()
    def OutgoingAgent(self, data) -> None:
        """
        Agent to pass data from PyQt thread to async GATT client
        """
        self.outgoingQueue.put(data)


    async def GATTSend(self, client: BleakClient, data) -> None:
        """
        Send data via GATT client
        """
        characteristic = client.services.get_characteristic(COMMAND_WRITE_UUID)
        commandMTU = characteristic.max_write_without_response_size//2
        if len(data) > commandMTU:
            print('More data than mtu, remove oldest commands')
            # If there are too many commands, remove the oldest ones
            data = data[(len(data) - commandMTU):]

        CommandBytes = [byte for command_data in data for byte in command_data]
        dataBytes = bytearray(CommandBytes)
        await client.write_gatt_char(characteristic, dataBytes)


    async def GATTClientMain(self) -> None:
        """
        Main loop for async GATT Client
        """
        while self.running:
            self.statusSignal.emit('Not connected') # Inform that client has disconnected
            print('Connecting to server...')
            try:
                async with BleakClient(self.HOST, timeout=1) as client: # Try to establish connection with server
                    self.statusSignal.emit('Connected') # Inform that the client is connected
                    characteristic = client.services.get_characteristic(COMMAND_WRITE_UUID)
                    if characteristic is None: client.disconnect()
                    await client.start_notify(characteristic, self.BLENotificationCB)
                    while self.running:
                        if not self.outgoingQueue.empty():
                            await self.GATTSend(client, self.outgoingQueue.get())
                        asyncio.sleep(1) # Keep connection open
            except:
                print('Could not establish connection')

    def run(self) -> None:
        """
        Main func for QThread
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.GATTClientMain())
        loop.close()

                

