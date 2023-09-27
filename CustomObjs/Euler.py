
import numpy as np
import sympy as sp

def EulerAngles(q):
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(q[0]), -np.sin(q[0])],
        [0, np.sin(q[0]), np.cos(q[0])]
    ])
    
    Ry = np.array([
        [np.cos(q[1]), 0, np.sin(q[1])],
        [0, 1, 0],
        [-np.sin(q[1]), 0, np.cos(q[1])]
    ])

    Rz = np.array([
        [np.cos(q[2]), -np.sin(q[2]), 0],
        [np.sin(q[2]), np.cos(q[2]), 0],
        [0, 0, 1]
    ])

    return Rx@Ry@Rz
    
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