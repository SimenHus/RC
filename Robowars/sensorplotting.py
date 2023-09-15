import matplotlib.pyplot as plt
import numpy as np
from SensorData import SensorData
from RobotModel import RobotModel

import sys
import os

filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{filePath}\\..')
from CustomObjs.Quaternion import Quaternion


class DataAnalyzis:
    def openFile(self, path, filename):
        file = f'{path}\\{filename}'
        with open(file, 'rb') as f: a = np.load(f)

        MAX_VAL = 2**15
        ACCEL_RANGE = MAX_VAL/16
        GYRO_RANGE = MAX_VAL/2000
        MAGNET_RANGE = MAX_VAL/4900

        def Rx(theta):
            Rx = np.array([
                [1, 0, 0],
                [0, np.cos(theta), -np.sin(theta)],
                [0, np.sin(theta), np.cos(theta)]
            ])
            return Rx

        def Rz(theta):
            Rz = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1]
            ])
            return Rz

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
        
        data = rotateData(data, Rz(np.pi/2))

        return data


    def getYawFromMag(self, mag, r, p):
        magX = mag[:, 0]*np.cos(p) + mag[:, 1]*np.sin(r) * \
            np.sin(p) + mag[:, 2]*np.cos(r)*np.sin(p)
        magY = -mag[:, 1]*np.cos(r) + mag[:, 2]*np.sin(r)

        yRaw = np.arctan2(magY, magX)
        return yRaw
    

    def plotData(self, t, data, plotInfo, title='title'):

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

    def getEuler(self, data):
        acc = data['acc']
        mag = data['mag']
        if len(acc.shape) < 2: acc = acc.reshape((1, 3))
        if len(mag.shape) < 2: mag = mag.reshape((1, 3))
        r = np.arctan2(acc[:, 1], acc[:, 2])
        p = -np.arctan2(acc[:, 0], np.sqrt(acc[:, 1]**2 + acc[:, 2]**2))
        y = obj.getYawFromMag(mag, r, p)
        return r, p, y

    def initQuat(self, data):
        r, p, y = self.getEuler(data)

        qMeasured = Quaternion([r, p, y])
        qMeasured.normalize()
        return qMeasured


    def storeRv(self, data):
        sampleSize = data['acc'].shape[0]
        gyro = data['gyro']

        r, p, y = self.getEuler(data)

        quat = np.vstack([Quaternion((r[i], p[i], y[i])).q() for i in range(len(r))])

        sample = np.zeros((sampleSize, 7))
        sample[:, :4] = quat
        sample[:, 4:] = gyro
        with open(f'{filePath}\\sensordata\\Rv.npy', 'wb') as f:
            np.save(f, sample)


pth = f'{filePath}\\sensordata'
title = 'positiv-yaw'
file = f'test-til-simen\\{title}.npy'
obj = DataAnalyzis()
rawData = obj.openFile(pth, file)
# obj.storeRv(rawData)

currentData = {}
for key, value in rawData.items():
    if key == 't': continue
    currentData[key] = value[0, :]
q0 = obj.initQuat(currentData)
x0 = np.hstack(([0]*3, q0.q(), [0]*3, currentData['gyro']))
dt = 1e-3
model = RobotModel
# Initialize sensor reader and kalman filter
sensorData = SensorData(dt, model, x0)

filteredData = sensorData.sample(np.array([0]*6), currentData)  # Sample filter
for i in range(1, len(rawData['t'])):
    for key, value in rawData.items():
        if key == 't': continue
        currentData[key] = value[i, :]
    state = sensorData.sample(np.array([0]*6), currentData)  # Sample filter
    for key, value in filteredData.items():
        if key == 't': continue
        filteredData[key] = np.vstack((value, state[key]))



filteredData['rawEuler'] = np.vstack(obj.getEuler(rawData)).T
filteredData['rawW'] = rawData['gyro']
filteredData['rawMag'] = rawData['mag']

plotInfo = {
    0: {'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw']},
    0: {'euler': ['Roll', 'Pitch', 'Yaw'],
        'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw']},
    1: {'rawW': ['Raw rollrate', 'Raw pitchrate', 'Raw yawrate'],
        'w': ['Rollrate', 'Pitchrate', 'Yawrate']},
}
obj.plotData(rawData['t'], filteredData, plotInfo, title=title)

