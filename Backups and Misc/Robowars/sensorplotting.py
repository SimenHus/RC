import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')

import matplotlib.pyplot as plt
import numpy as np
from Robowars.Measurement import Filter
from CustomObjs.SensorFuncs import IMUFuncs
from CustomObjs.Euler import Rx, Rz


def openFile(path, filename):
    file = f'{path}\\{filename}'
    with open(file, 'rb') as f: a = np.load(f)

    MAX_VAL = 2**15
    ACCEL_RANGE = MAX_VAL/16
    GYRO_RANGE = MAX_VAL/2000
    MAGNET_RANGE = MAX_VAL/4900

    data = {}
    data['t'] = (a[:, 0] - a[0, 0])/1000
    data['acc'] = a[:, 1:4]/ACCEL_RANGE
    data['gyro'] = a[:, 4:7]/GYRO_RANGE*(np.pi/180)
    data['mag'] = a[:, 7:10]/MAGNET_RANGE
    data['mag'] = (Rx(np.pi)@data['mag'].T).T

    def rotateData(data, R):
        newData = {}
        for key, value in data.items():
            if len(value.shape) < 2: newData[key] = value
            else: newData[key] = (R@value.T).T
        return newData
    
    data = rotateData(data, Rz(np.pi/2)) # 90 degree yaw

    return data
    

def plotData(t, data, plotInfo, title='title'):

    fig, axs = plt.subplots(len(plotInfo), 3)
    for i, categories in plotInfo.items():
        for category, labels in categories.items():
            for j in range(3):
                axs[i, j].plot(t, data[category][:, j], label=labels[j])

    for row in axs:
        for ax in row:
            ax.grid()
            ax.legend()
    plt.suptitle(title)
    plt.show()



pth = f'{filePath}\\sensordata'
title = 'positiv-yaw'
file = f'test-til-simen\\{title}.npy'
IMU = IMUFuncs()
rawData = openFile(pth, file)

currentData = {}
for key, value in rawData.items():
    if key == 't': continue
    currentData[key] = value[0, :]
r0, p0, y0 = IMU.getAngles(currentData)
x0 = np.hstack((r0, p0, y0, currentData['gyro']))
P0 = np.eye(6)
dt = 1e-3
# Initialize kalman filter
sensorData = Filter(dt, x0, P0)

filteredData = sensorData.sample(np.array([0]*6), currentData)  # Sample filter
for i in range(1, len(rawData['t'])):
    for key, value in rawData.items():
        if key == 't': continue
        currentData[key] = value[i, :]
    state = sensorData.sample(np.array([0]*6), currentData)  # Sample filter
    for key, value in filteredData.items():
        if key == 't': continue
        filteredData[key] = np.vstack((value, state[key]))



filteredData['rawEuler'] = np.vstack(IMU.getAngles(rawData)).T
filteredData['rawW'] = rawData['gyro']
filteredData['rawMag'] = rawData['mag']

plotInfo = {
    0: {'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw']},
    0: {'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw'], 
        'q': ['Roll', 'Pitch', 'Yaw']},
    1: {'rawW': ['Raw rollrate', 'Raw pitchrate', 'Raw yawrate']},
    1: {'rawW': ['Raw rollrate', 'Raw pitchrate', 'Raw yawrate'],
        'w': ['Rollrate', 'Pitchrate', 'Yawrate']},
}
plotData(rawData['t'], filteredData, plotInfo, title=title)

