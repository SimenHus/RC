
from CustomObjs.Quaternion import Quaternion
import numpy as np

q1 = Quaternion(1, np.array([0]*3))

q2 = Quaternion(0.5, np.array([0.5]*3))

print(q1@q1)