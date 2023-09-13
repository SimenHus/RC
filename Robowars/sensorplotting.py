import matplotlib.pyplot as plt
import numpy as np
from SensorData import SensorData
from RobotModel import RobotModel

from CustomObjs.Quaternion import Quaternion


class DataAnalyzis:
    def openFile(self, path, filename):
        file = f'{path}\\{filename}'
        with open(file, 'rb') as f: a = np.load(f)

        MAX_VAL = 2**15
        ACCEL_RANGE = MAX_VAL/16
        GYRO_RANGE = MAX_VAL/2000
        MAGNET_RANGE = MAX_VAL/4900

        Rx = np.array([
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, -1]
        ])

        data = {}
        data['t'] = (a[:, 0] - a[0, 0])/1000
        data['acc'] = a[:, 1:4]/ACCEL_RANGE
        data['gyro'] = a[:, 4:7]/GYRO_RANGE*(np.pi/180)
        data['mag'] = a[:, 7:10]/MAGNET_RANGE

        data['mag'] = (Rx@data['mag'].T).T

        return data


    def getYawFromMag(self, magRaw, rRaw, pRaw):
        magX = magRaw[:, 0]*np.cos(pRaw) + magRaw[:, 1]*np.sin(rRaw) * \
            np.sin(pRaw) + magRaw[:, 2]*np.cos(rRaw)*np.sin(pRaw)
        magY = -magRaw[:, 1]*np.cos(rRaw) + magRaw[:, 2]*np.sin(rRaw)

        yRaw = -np.arctan2(magY, magX)
        return yRaw
    

    def plotData(self, t, data, plotInfo):

        fig, axs = plt.subplots(len(plotInfo), 3)
        for i, categories in plotInfo.items():
            for category, labels in categories.items():
                for j in range(3):
                    axs[i, j].plot(t, data[category][:, j], label=labels[j])

        for row in axs:
            for ax in row:
                ax.grid()
                ax.legend()
        plt.show()


    def initQuat(self, data):
        accRaw = data['acc']
        magRaw = data['mag']
        # If IMU is not in the CoG, transformation needs to be done

        # Convert sensor readings to y
        r = np.arctan2(accRaw[1], np.sqrt(accRaw[0]**2 + accRaw[2]**2))
        p = np.arctan2(accRaw[0], np.sqrt(accRaw[1]**2 + accRaw[2]**2))
        # Assuming IMU in CoG

        mag_x = magRaw[0]*np.cos(p) + magRaw[1]*np.sin(r) * \
            np.sin(p) + magRaw[2]*np.cos(r)*np.sin(p)
        mag_y = magRaw[1]*np.cos(r) - magRaw[2]*np.sin(r)
        y = np.arctan2(-mag_y, mag_x)

        qMeasured = Quaternion([r, p, y])
        qMeasured.normalize()
        return qMeasured


    def storeRv(self, data):
        sampleSize = data['acc'].shape[0]
        accRaw = data['acc']
        magRaw = data['mag']
        gyroRaw = data['gyro']

        rRaw = np.arctan2(accRaw[:, 1], accRaw[:, 2])
        pRaw = np.arctan2(accRaw[:, 0], np.sqrt(accRaw[:, 1]**2 + accRaw[:, 2]**2))

        yRaw = self.getYawFromMag(magRaw, rRaw, pRaw)

        def fromEulerAngles(euler):
            r, p, y = euler
            def c(_): return np.cos(_)
            def s(_): return np.sin(_)

            # Euler angles to quaternions
            quat = np.array([
                c(r)*c(p)*c(y) + s(r)*s(p)*s(y),
                s(r)*c(p)*c(y) - c(r)*s(p)*s(y),
                c(r)*s(p)*c(y) + s(r)*c(p)*s(y),
                c(r)*c(p)*s(y) - s(r)*s(p)*c(y),
            ]).reshape((r.shape[0], 4))
            return quat

        quatRaw = fromEulerAngles((rRaw, pRaw, yRaw))

        sample = np.zeros((sampleSize, 7))
        sample[:, :4] = quatRaw
        sample[:, 4:] = gyroRaw
        with open('C:\\Users\\simen\\Desktop\\Prog\\Python\\Robowars\\sensordata\\Rv.npy', 'wb') as f:
            np.save(f, sample)


pth = 'C:\\Users\\simen\\Desktop\\Prog\\Python\\Robowars\\sensordata'
file = 'test-til-simen\\spinning.npy'
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



accRaw = rawData['acc']
magRaw = rawData['mag']

rRaw = np.arctan2(accRaw[:, 1], accRaw[:, 2])
pRaw = np.arctan2(accRaw[:, 0], np.sqrt(accRaw[:, 1]**2 + accRaw[:, 2]**2))
yRaw = obj.getYawFromMag(magRaw, rRaw, pRaw)

filteredData['rawEuler'] = np.vstack((rRaw, pRaw, yRaw)).T
filteredData['rawW'] = rawData['gyro']
filteredData['rawMag'] = rawData['mag']

plotInfo = {
    0: {'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw']},
    # 0: {'euler': ['Roll', 'Pitch', 'Yaw']},
        # 'rawEuler': ['Raw roll', 'Raw pitch', 'Raw yaw']},
    1: {'rawW': ['Raw rollrate', 'Raw pitchrate', 'Raw yawrate'],
        'w': ['Rollrate', 'Pitchrate', 'Yawrate']},
    2: {'rawMag': ['magx', 'magy', 'magz']} 
}
obj.plotData(rawData['t'], filteredData, plotInfo)

