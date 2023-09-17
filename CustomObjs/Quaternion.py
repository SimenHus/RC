
import numpy as np

class Quaternion:
    def __init__(self, q0=np.array([1, 0, 0, 0])):
        if len(q0) == 3: q0 = self.fromEulerAngles(q0)
        elif q0.dtype == 'int32': q0 = q0.astype('float64')
        self.__q = self.normalize(q0)

    def q(self): return self.__q
    def w(self): return self.__q[0]
    def x(self): return self.__q[1]
    def y(self): return self.__q[2]
    def z(self): return self.__q[3]

    def fromEulerAngles(self, euler):
        # Using 3-2-1 euler sequence
        r, p, y = euler

        cr, sr = np.cos(r/2), np.sin(r/2)
        cp, sp = np.cos(p/2), np.sin(p/2)
        cy, sy = np.cos(y/2), np.sin(y/2)

        # Euler angles to quaternions
        quat = np.array([
            cr*cp*cy + sr*sp*sy,
            sr*cp*cy - cr*sp*sy,
            cr*sp*cy - sr*sp*cy,
            cr*cp*sy - sr*sp*cy
        ]).reshape((4,))
        return quat

    def toEulerAngles(self, order='ZYX'):
        qw, qx, qy, qz = self.__q
        if order=='ZYX':
            # To 3-2-1 euler sequence
            roll = np.arctan2(2*(qw*qx+qy*qz), 1-2*(qx**2+qy**2))
            pitch = -np.pi/2 + 2*np.arctan2(1+2*(qw*qy-qx*qz), 1-2*(qw*qy-qx*qz))
            yaw = np.arctan2(2*(qw*qz+qx*qy), 1-2*(qy**2+qz**2))
        if order=='XYZ':
            # 1-2-3 sequence
            roll = np.arctan2(2*(qy*qz+qw*qx), qw**2-qx**2-qy**2+qz**2)
            pitch = np.arcsin(-2*(qx*qz-qw*qy))
            yaw = np.arctan2(2*(qx*qy+qw*qz), qw**2+qx**2-qy**2-qz**2)

        return np.array([roll, pitch, yaw])
    
    def toRPY(self):
        qw, qx, qy, qz = self.__q
        roll = np.arctan2(2*(qw*qx+qy*qz), 1-2*(qx**2+qy**2))
        pitch = -np.pi/2 + 2*np.arctan2(1+2*(qw*qy-qx*qz), 1-2*(qw*qy-qx*qz))
        yaw = np.arctan2(2*(qw*qz+qx*qy), 1-2*(qy**2+qz**2))

        return -np.array([roll, pitch, yaw])
    

    # Alternative way of getting the quaternion, see https://ahrs.readthedocs.io/en/latest/filters/aqua.html
    def qAcc(self, acc):
        ax, ay, az = acc
        if az >= 0: qAcc = np.array([np.sqrt((az+1)/2), -ay/np.sqrt(2*az+2), ax/np.sqrt(2*az+2), 0]) 
        else:       qAcc = np.array([-ay/np.sqrt(2-2*az), np.sqrt((1-az)/2), 0, ax/np.sqrt(2-2*az)])
        qAcc = Quaternion(qAcc)
        return qAcc
    
    def qMag(self, qAcc, mag: np.ndarray):
        l = qAcc.toRotationMatrix().T@mag
        lx, ly, lz = l
        gamma = lx**2 + ly**2
        if lx >= 0: qMag = np.array([np.sqrt(gamma+lx*np.sqrt(gamma))/np.sqrt(2*gamma), 0, 0, ly/(np.sqrt(2)*np.sqrt(gamma+lx*np.sqrt(gamma)))])
        else:       qMag = np.array([ly/(np.sqrt(2)*np.sqrt(gamma-lx*np.sqrt(gamma))), 0, 0, np.sqrt(gamma-lx*np.sqrt(gamma))/np.sqrt(2*gamma)])
        qMag = Quaternion(qMag)
        return qMag
    
    
    def toRotationMatrix(self, q=None):
        if q is None: q = self.__q
        nu, e1, e2, e3 = q

        R = np.array([
            [nu**2 + e1**2 - e2**2 - e3**2, 2 *
                (e1*e2 - nu*e3), 2*(e1*e3 + nu*e2)],
            [2*(e1*e2 + nu*e3), nu**2 - e1**2 +
                e2**2 - e3**2, 2*(e2*e3 - nu*e1)],
            [2*(e1*e3 - nu*e2), 2*(e2*e3 + nu*e1), nu**2 - e1**2 - e2**2 + e3**2]
        ])
        return R
    
    def skew(self, vector):
        skewMatrix = np.array([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix

    def normalize(self, q=None):
        if q is None:
            self.__q /= np.linalg.norm(self.__q)
            q = self.__q
        else: q /= np.linalg.norm(q)
        return q
    
    def conjugate(self, q=None):
        if q is None: q = self.__q
        return np.hstack((q[0], -q[1:]))
    
    def quaternionMultiplication(self, q1, q2):
        nu1 = q1[0]
        eps1 = np.array(q1[1:])
        nu2 = q2[0]
        eps2 = np.array(q2[1:])

        m1 = np.vstack((
            np.hstack((nu1, -eps1.T)),
            np.hstack((eps1.reshape((3, 1)), nu1*np.eye(3) + self.skew(eps1)))
        ))
        m2 = np.hstack((nu2, eps2))
        return m1@m2

    def coordinateTransform(self, q, w):
        nu = q[0]
        eps = np.array(q[1:])
        U = np.vstack(
            -eps.T,
            nu*self.I3x3 + self.skew(eps)
        )
        return U@w

    def __add__(self, q):
        return self.__q + q
    
    def __iter__(self):
        for x in self.__q: yield x

    def __mul__(self, obj):
        if type(obj) == Quaternion: return Quaternion(self.quaternionMultiplication(self.__q, obj.q()))
        if type(obj) == np.ndarray and len(obj) == 3: return self.coordinateTransform(self.__q, obj)
        if type(obj) == float or int: return Quaternion(self.__q*obj)
