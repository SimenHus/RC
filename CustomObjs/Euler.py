
import numpy as np

def Rx(theta):
    R = np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])
    return R

def Ry(theta):
    R = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    return R

def Rz(theta):
    R = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])
    return R

def RxDiff(theta):
    R = np.array([
        [0, 0, 0],
        [0, -np.sin(theta), -np.cos(theta)],
        [0, np.cos(theta), -np.sin(theta)]
    ])
    return R

def RyDiff(theta):
    R = np.array([
        [-np.sin(theta), 0, np.cos(theta)],
        [0, 0, 0],
        [-np.cos(theta), 0, -np.sin(theta)]
    ])
    return R

def RzDiff(theta):
    R = np.array([
        [-np.sin(theta), -np.cos(theta), 0],
        [np.cos(theta), -np.sin(theta), 0],
        [0, 0, 0]
    ])
    return R


def EulerAngles(q):
    return Rx(q[0])@Ry(q[1])@Rz(q[2])

def EulerAngleStateJacobian(q, x):
    J1 = (RxDiff(q[0])@Ry(q[1])@Rz(q[2])@x).reshape((3, 1))
    J2 = (Rx(q[0])@RyDiff(q[1])@Rz(q[2])@x).reshape((3, 1))
    J3 = (Rx(q[0])@Ry(q[1])@RzDiff(q[2])@x).reshape((3, 1))
    return np.hstack((J1, J2, J3))
    