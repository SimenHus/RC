
import numpy as np
import sympy as sp

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

def EulerAngles(q):
    return Rx(q[0])@Ry(q[1])@Rz(q[2])
    
def EulerAnglesSymb(q):
    Rx = sp.Matrix([
        [1, 0, 0],
        [0, sp.cos(q[0]), -sp.sin(q[0])],
        [0, sp.sin(q[0]), sp.cos(q[0])]
    ])
    
    Ry = sp.Matrix([
        [sp.cos(q[1]), 0, sp.sin(q[1])],
        [0, 1, 0],
        [-sp.sin(q[1]), 0, sp.cos(q[1])]
    ])

    Rz = sp.Matrix([
        [sp.cos(q[2]), -sp.sin(q[2]), 0],
        [sp.sin(q[2]), sp.cos(q[2]), 0],
        [0, 0, 1]
    ])

    return Rz*Ry*Rx