
import numpy as np

from dataclasses import dataclass


@dataclass
class Quaternion:
    """Class representing a quaternion.

    Args:
        eta (float): Eta/w/real part
        epsilon (ndarray[3]): Epsilon/xyz/imaginary part
    """
    
    eta: float
    eps: 'np.ndarray[3]'

    def __post_init__(self) -> None:
        norm = np.sqrt(self.eta**2 + sum(self.eps**2))
        if not np.allclose(norm, 1):
            self.eta /= norm
            self.eps /= norm
        if self.eta < 0:
            self.eta *= -1
            self.eps *= -1

    def toEulerAngles(self) -> 'np.ndarray[3]':
        """
        Returns the quaternion represented in euler angles
        """
        qw, epsilon = self
        qx, qy, qz = epsilon
        # To 3-2-1 euler sequence (ZYX)
        roll = np.arctan2(2*(qw*qx+qy*qz), 1-2*(qx**2+qy**2))
        pitch = -np.pi/2 + 2*np.arctan2(1+2*(qw*qy-qx*qz), 1-2*(qw*qy-qx*qz))
        yaw = np.arctan2(2*(qw*qz+qx*qy), 1-2*(qy**2+qz**2))

        # 1-2-3 sequence (XYZ)
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

    
    def toRotationMatrix(self) -> 'np.ndarray[3, 3]':
        """
        Returns quaternion rotation represented as rotation matrix
        """
        eta, eps = self
        e1, e2, e3 = eps

        R = np.array([
            [eta**2 + e1**2 - e2**2 - e3**2, 2 *
                (e1*e2 - eta*e3), 2*(e1*e3 + eta*e2)],
            [2*(e1*e2 + eta*e3), eta**2 - e1**2 +
                e2**2 - e3**2, 2*(e2*e3 - eta*e1)],
            [2*(e1*e3 - eta*e2), 2*(e2*e3 + eta*e1), eta**2 - e1**2 - e2**2 + e3**2]
        ])
        return R
    
    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.eta, -self.eps)
    
    def diff(self, other: 'Quaternion') -> 'Quaternion':
        """
        Return difference between two quaternions
        """
        return self.conjugate().multiply(other)
    
    def multiply(self, other: 'Quaternion') -> 'Quaternion':
        eta, eps = self

        m1 = np.vstack((
            np.hstack((eta, -eps.T)),
            np.hstack((eps.reshape((3, 1)), eta*np.eye(3) + self.skew(eps)))
        ))
        m2 = np.hstack((other.eta, other.eps))
        result = m1@m2
        return Quaternion(result[0], result[1:])

    def coordinateTransform(self, other) -> 'Quaternion':
        eta, eps = self
        U = np.vstack(
            -eps.T,
            eta*np.eye(3) + self.skew(eps)
        )
        result = U@other
        return Quaternion(result[0], result[1:])
    

    # Alternative way of getting the quaternion, see https://ahrs.readthedocs.io/en/latest/filters/aqua.html
    @staticmethod
    def fromAccelerometer(acc: 'np.ndarray[3]') -> 'Quaternion':
        """
        Get quaternion representation from accelerometer
        """
        ax, ay, az = acc
        if az >= 0: qAcc = np.array([np.sqrt((az+1)/2), -ay/np.sqrt(2*az+2), ax/np.sqrt(2*az+2), 0]) 
        else:       qAcc = np.array([-ay/np.sqrt(2-2*az), np.sqrt((1-az)/2), 0, ax/np.sqrt(2-2*az)])
        return Quaternion(qAcc[0], qAcc[1:])
    
    @staticmethod
    def fromMagnetometer(qAcc: 'Quaternion', mag: 'np.ndarray[3]') -> 'Quaternion':
        """
        Get quaternion representation from accelerometer quaternion and magnetometer
        """
        l = qAcc.R.T@mag
        lx, ly, lz = l
        gamma = lx**2 + ly**2
        if lx >= 0: qMag = np.array([np.sqrt(gamma+lx*np.sqrt(gamma))/np.sqrt(2*gamma), 0, 0, ly/(np.sqrt(2)*np.sqrt(gamma+lx*np.sqrt(gamma)))])
        else:       qMag = np.array([ly/(np.sqrt(2)*np.sqrt(gamma-lx*np.sqrt(gamma))), 0, 0, np.sqrt(gamma-lx*np.sqrt(gamma))/np.sqrt(2*gamma)])
        return Quaternion(qMag[0], qMag[1:])

    @staticmethod
    def fromEulerAngles(euler: 'np.ndarray[3]') -> 'Quaternion':
        """
        Returns a Quaternion object derived from euler angles
        """
        # Using 3-2-1 euler sequence
        r, p, y = euler

        cr, sr = np.cos(r/2), np.sin(r/2)
        cp, sp = np.cos(p/2), np.sin(p/2)
        cy, sy = np.cos(y/2), np.sin(y/2)

        # Euler angles to quaternions
        q = np.array([
            cr*cp*cy + sr*sp*sy,
            sr*cp*cy - cr*sp*sy,
            cr*sp*cy - sr*sp*cy,
            cr*cp*sy - sr*sp*cy
        ]).reshape((4,))
        return Quaternion(q[0], q[1:])
    

    @staticmethod
    def skew(vector):
        skewMatrix = np.array([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix
    
    @property
    def R(self) -> 'np.ndarray[3, 3]': return self.toRotationMatrix()
    @property
    def w(self): return self.eta
    @property
    def x(self) -> float: return self.eps[0]
    @property
    def y(self) -> float: return self.eps[1]
    @property
    def z(self) -> float: return self.eps[3]


    def __repr__(self):
        return f'\u03B7 = {self.eta}, \u03B5 = {self.eps}'

    def __add__(self, other: 'Quaternion') -> 'Quaternion':
        return Quaternion(self.eta + other.eta, self.eps + other.eps)
    
    def __iter__(self):
        return iter([self.eta, self.eps])

    def __mul__(self, other) -> 'Quaternion':
        """
        Perform operation depending on type of other
        """
        if type(other) == Quaternion: return self.multiply(other)
        if type(other) == np.ndarray and len(other) == 3: return self.coordinateTransform(other)
        if type(other) == float or int: return Quaternion(self.eta*other, self.eps*other)

    def __matmul__(self, other) -> 'Quaternion':
        return self.multiply(other)

