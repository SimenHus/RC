import asyncio
from struct import unpack
import numpy as np

from bleak import BleakClient, BleakScanner, BLEDevice
from PySide6.QtCore import QThread, Signal, Slot, Qt


# Hentet fra Schimen sim kode
COMMAND_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
COMMAND_WRITE_UUID  = "12345678-1234-5678-1234-56789abcdef1"
DEBUG_SERVICE_UUID =    "deb12345-1234-5678-1234-56789abcdefa"
DEBUG_READ_UUID =       "deb12345-1234-5678-1234-56789abcdefb"

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


class Client(QThread):
    dataSignal = Signal(list)
    statusSignal = Signal(str)

    def __init__(self, host='rupert', port=4, *args, **kwargs):
        """
        host: str - Host MAC address to connect to
        port: int - Port to connect to
        """
        super().__init__(*args, **kwargs)

        self.outgoingQueue = asyncio.Queue()
        self.writeCommandId = 0

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

    def debugCB(self, _, data):
        debugInfo = unpack('< q hhh hhh hhh h xxxx', data)
        self.dataSignal.emit(debugInfo)


    @Slot()
    def OutgoingAgent(self, activeButtonList: set) -> None:
        """
        Agent to pass data from PyQt thread to async GATT client
        """
        forceDir = [0, 0]
        if Qt.Key_Right in activeButtonList: forceDir[1] += 1 # (Forward, Clockwise rotation)
        if Qt.Key_Left in activeButtonList: forceDir[1] += -1 # (Forward, Clockwise rotation)
        if Qt.Key_Up in activeButtonList: forceDir[0] += 1 # (Forward, Clockwise rotation)
        if Qt.Key_Down in activeButtonList: forceDir[0] += -1 # (Forward, Clockwise rotation)
        Kf, rw = 1, 1 # Motor force constant and distance from CoG to wheels
        forward, clockwiseRotation = forceDir
        Vs = clockwiseRotation/(Kf*rw)
        Vd = forward/Kf

        maxFromMiddle = 5
        V1 = int(1/2*(Vs + Vd)*maxFromMiddle + 127)
        V2 = int(1/2*(Vs - Vd)*maxFromMiddle + 127)
        
        asyncio.run(self.outgoingQueue.put((LEFT_MOTOR_COMMAND, V1)))
        asyncio.run(self.outgoingQueue.put((RIGHT_MOTOR_COMMAND, V2)))
        print(V1, V2)


    async def GATTSend(self, client: BleakClient, msg: tuple) -> None:
        """
        Send data via GATT client
        """
        key, value = msg
        head = 0xFF & ((key << 5) | self.writeCommandId)
        data = bytearray([head, value])
        await client.write_gatt_char(COMMAND_WRITE_UUID, data)
        self.writeCommandId += 1


    async def findHost(self) -> None:
        # correct_device = lambda d, _: 'rupert' in d.name.lower()
        # device = await BleakScanner.find_device_by_filter(
        #     correct_device,
        #     timeout=5
        # )
        device = await BleakScanner.find_device_by_name(self.HOST, timeout=3)
        return device

    async def GATTClientMain(self) -> None:
        """
        Main loop for async GATT Client
        """
        while self.running:
            self.statusSignal.emit('Not connected') # Inform that client has disconnected
            device = None
            while self.running and device is None: device: BLEDevice = await self.findHost()
            if not self.running: break

            async with BleakClient(device.address, timeout=5) as client: # Try to establish connection with server
                self.statusSignal.emit('Connected') # Inform that the client is connected
                characteristic = client.services.get_characteristic(DEBUG_READ_UUID)
                if characteristic is None: client.disconnect()
                await client.start_notify(characteristic, self.debugCB)
                while self.running:
                    if not self.outgoingQueue.empty():
                        await self.GATTSend(client, await self.outgoingQueue.get())
                    await asyncio.sleep(0.001)

    def run(self) -> None:
        """
        Main func for QThread
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.GATTClientMain())
        loop.close()

                

