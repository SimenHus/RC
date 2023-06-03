import numpy as np

class Controller:
    'Controller module'
    def __init__(self):
        
        # Controller params
        self.Kpx = 1 # Gain linear Kp
        self.Kptheta = 0.1 # Gain angular Kp
        self.Kdc = 4 # Gain all Kd
        self.I3x3 = np.eye(3)

    def sample(self, state, dState):
        q = state['q']
        qd = dState['angle']
        qTilde = self.normalize(self.qMul(self.conjugate(qd), q))

        nu = np.hstack((state['v'], state['w']))
        nud = np.hstack((dState['linVel'], dState['angVel']))

        R = state['R']
        zTilde = np.hstack((state['x'] - dState['pos'], self.signum(q[0])*qTilde[1:]))
        nuTilde = nu - nud
        Kp = self.Kp(R)
        Kd = self.Kd()
        tau = -Kd@nuTilde - Kp@zTilde
        
        return tau
          

    def R(self, theta):
        c1 = np.cos(theta[0] * np.pi / 180)
        s1 = np.sin(theta[0] * np.pi / 180)
        c2 = np.cos(theta[1] * np.pi / 180)
        s2 = np.sin(theta[1] * np.pi / 180)
        c3 = np.cos(theta[2] * np.pi / 180)
        s3 = np.sin(theta[2] * np.pi / 180)

        matrix = np.array([[c2*c3, -c2*s3, s2],
                           [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
                           [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]])
        return matrix
    
    def conjugate(self, q):
        q[1:] = -q[1:]
        return q
    
    def qMul(self, q1, q2):
        lMatrix = np.vstack((
            np.array([q1[0]] + list(-q1[1:])),
            np.hstack((q1[1:].reshape(3, 1), q1[0]*self.I3x3+self.skew(q1[1:])))
        ))
        return lMatrix@q2

    def normalize(self, q):
        return q/np.linalg.norm(q)
    
    def signum(self, x):
        return 1 if x >=0 else -1

    def Kp(self, R):
        R = R.T@self.I3x3
        return np.vstack((np.hstack((R*self.Kpx, np.zeros((3, 3)))),
                          np.hstack((np.zeros((3, 3)), R*self.Kptheta))))
    
    def Kd(self):
        return np.diag([1]*6)*self.Kdc
    
    def skew(self, vector):
        skewMatrix = np.array([
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ])
        return skewMatrix