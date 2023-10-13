
import numpy as np

class IMUFuncs:
    def getAngles(self, data):
        acc = data['acc']
        mag = data['mag']
        if len(acc.shape) < 2: acc = acc.reshape((1, 3))
        if len(mag.shape) < 2: mag = mag.reshape((1, 3))
        r = np.arctan2(acc[:, 1], acc[:, 2])
        p = np.arctan2(-acc[:, 0], np.sqrt(acc[:, 1]**2 + acc[:, 2]**2))
        y = self.getYawFromMag(mag, r, p)
        return r, p, y

    def getYawFromMag(self, mag, r, p):
        magX = mag[:, 0]*np.cos(p) + mag[:, 1]*np.sin(r) * \
            np.sin(p) + mag[:, 2]*np.cos(r)*np.sin(p)
        magY = -mag[:, 1]*np.cos(r) + mag[:, 2]*np.sin(r)

        y = np.arctan2(magY, magX)

        # magX = mag[:, 0]*np.cos(r) + mag[:, 1]*np.sin(r) * \
        #     np.sin(p) + mag[:, 2]*np.sin(r)*np.cos(p)
        # magY = mag[:, 1]*np.cos(p) - mag[:, 2]*np.sin(p)

        # y = np.arctan2(-magY, magX)
        return y