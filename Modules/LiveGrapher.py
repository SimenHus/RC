import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import randint
from multiprocessing import Process
from time import sleep, time

class Grapher(Process):

    def __init__(self, dt: float):
        super().__init__()
        self.maxPoints = 100

        self.dt = dt
        self.t = [-self.maxPoints+i*self.dt for i in range(self.maxPoints)]
        
        self.data = {}
        self.fig = plt.figure()
        self.subplots = []

    def addSubplot(self, dataNames: list):
        index = int(f'22{len(self.subplots)+1}')
        ax = self.fig.add_subplot(index)
        inits = [0]*self.maxPoints
        dataElements = {elem: inits for i, elem in enumerate(dataNames)}

        for elem, value in dataElements.items():
            ax.plot(self.t, value, label=elem)

        ax.grid()
        ax.legend()

        self.data.update(dataElements)

        self.subplots.append(ax)

    def run(self):
        ani = animation.FuncAnimation(self.fig,
                                      self.anim,
                                      interval=1,
                                      blit=True)
        plt.show()

    def anim(self):
        for ax in self.subplots:
            ylim = ax.get_ylim()
            ax.set_xlim(self.t[0], self.t[-1])
            for line in ax.get_lines():
                lineData = line.get_ydata()
                if min(lineData) < ylim[0]:
                    ax.set_ylim(min(lineData), ylim[1])
                if max(lineData) > ylim[1]:
                    ax.set_ylim(ylim[0], max(lineData))
                
                line.set_data(self.t, self.data[line.get_label()])

    def addData(self, data: dict):
        
        size = len(data[list(data)[0]])
        
        for _ in range(size): self.t.append(self.t[-1]+self.dt)
        self.t = self.t[size:]

        for elem, value in data.items():
            self.data[elem] = self.data[elem] + value
            self.data[elem] = self.data[elem][size:]


tings = ['s', 'k']
tings2 = ['x', 'y', 'z']

app = Grapher(1)

app.addSubplot(tings)
app.addSubplot(tings2)


def main():
    while True:
        startTime = time()
        sampleSize = randint(1, 10)
        uptDict = {
            's': [randint(-100, 100)]*sampleSize,
            'k': [randint(-120, 80)]*sampleSize,
            'x': [randint(-100, 600)]*sampleSize,
            'y': [randint(-50, 130)]*sampleSize,
            'z': [randint(-120, 120)]*sampleSize,
        }
        app.addData(uptDict)
        elapsedTime = (time() - startTime)*1000
        print(f'Elapsed time: {elapsedTime:0.2f}ms')

if __name__ == '__main__':
    app.start()
    main()
    app.join()