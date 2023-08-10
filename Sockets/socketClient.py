
import socket
import numpy as np
from time import sleep
import pickle

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# python Desktop\Prog\Sockets\socketClient.py

nStates = 2
t = np.array([0])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    funcs = [np.sin, np.cos]
    states = []
    for i in range(nStates):
        # newState = {'Name': f'x{i+1}', 'x0': np.random.default_rng().standard_normal(1)*10}
        newState = {'Name': f'x{i+1}', 'x0': funcs[i%len(funcs)](t)}
        states.append(newState)
    connectMsg = {'MessageType': 'Init', 'Data': states}
    s.connect((HOST, PORT))
    s.sendall(pickle.dumps(connectMsg))
    sleep(1)
    while True:
        # data = [{'Name': f'x{i+1}', 'Measurement': np.random.default_rng().standard_normal(1)*10} for i in range(nStates)]
        data = [{'Name': f'x{i+1}', 'Measurement': funcs[i%len(funcs)](t*0.1)} for i in range(nStates)]
        dataMsg = {'MessageType': 'Data', 'Data': data}
        s.sendall(pickle.dumps(dataMsg))
        t[0] += 1
        sleep(0.1)
