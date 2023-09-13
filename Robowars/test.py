import sys
sys.path.insert(0, "C:\\Users\\simen\\Desktop\\Prog\\Python")
from CustomObjs.Quaternion import Quaternion

import numpy as np

q = Quaternion([180, 0, 0])

print(q.toRotationMatrix())
