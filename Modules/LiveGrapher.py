import matplotlib.pyplot as plt
import matplotlib.animation as animation
from multiprocessing import Process

import matplotlib
matplotlib.use('GTK3Agg') # Allowing remote showcase of plot for ssh

class Grapher(Process):

    def __init__(self, dt: float, queue):
        super().__init__()
        self.maxPoints = 100

        self.dt = dt
        self.t = [0]
        
        self.data = {}
        self.fig = plt.figure()
        self.subplots = []

        # Threading variables
        self.queue = queue
        self.daemon = True
        self.running = True

    def addSubplot(self, data: dict):
        index = int(f'22{len(self.subplots)+1}')
        ax = self.fig.add_subplot(index)

        newData = {}
        for name, inits in data.items():
            for i, dataset in enumerate(inits):
                label = f'{name}_{i+1}'
                ax.plot(self.t, [dataset], label=label)
                newData.update({label: [dataset]})

        ax.set_xlim(self.t[0], self.maxPoints*self.dt)
        ax.set_xlabel('t [s]')
        ax.grid()
        ax.legend()

        self.data.update(newData)
        self.subplots.append(ax)
        

    def run(self):
        ani = animation.FuncAnimation(self.fig,
                                      self.anim,
                                      interval=10,
                                      cache_frame_data=False)
        
        self.fig.show()
        self.queue.put('ready')
        while self.running: plt.pause(0.01)
        plt.close()

    def anim(self, *args):
        while not self.queue.empty():
            msg = self.queue.get()
            if msg[0] == 'data': self.addData(msg[1])
            elif msg[0] == 'exit': self.running = False

        for ax in self.subplots:
            ylim = ax.get_ylim()
            if len(self.t) >= self.maxPoints: ax.set_xlim(self.t[0], self.t[-1])
            for line in ax.get_lines():
                lineData = line.get_ydata()
                if min(lineData) < ylim[0]:
                    ax.set_ylim(min(lineData)*1.5, ylim[1])
                if max(lineData) > ylim[1]:
                    ax.set_ylim(ylim[0], max(lineData)*1.5)
                line.set_data(self.t, self.data[line.get_label()])
        

    def addData(self, data: dict):
        
        self.t.append(self.t[-1]+self.dt)
        if len(self.t) > self.maxPoints: self.t = self.t[1:]

        for elem, valueArray in data.items():
            for i, value in enumerate(valueArray):
                label = f'{elem}_{i+1}'
                if label not in self.data: break
                self.data[label] = self.data[label] + [value]
                if len(self.data[label]) > self.maxPoints:
                    self.data[label] = self.data[label][1:]

    def cleanup(self):
        self.queue.put(['exit'])