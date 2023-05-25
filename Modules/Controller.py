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
        z = np.hstack((state['x'], state['theta']))
        nu = np.hstack((state['v'], state['w']))
        zd = np.hstack((dState['pos'], dState['angle']))
        nud = np.hstack((dState['linVel'], dState['angVel']))

        R = self.R(state['theta'])

        zTilde = z - zd
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

    def Kp(self, R):
        R = R.T@self.I3x3
        return np.vstack((np.hstack((R*self.Kpx, np.zeros((3, 3)))),
                          np.hstack((np.zeros((3, 3)), R*self.Kptheta))))
    
    def Kd(self):
        return np.diag([1]*6)*self.Kdc
