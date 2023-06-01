import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import randint
from multiprocessing import Process, Queue
from time import sleep, time

class Grapher(Process):

    def __init__(self, dt: float, q: Queue):
        super().__init__()
        self.maxPoints = 100
        self.running = True

        self.q = q
        self.dt = dt
        self.t = [0]
        
        self.data = {}
        self.fig = plt.figure()
        self.subplots = []

    def addSubplot(self, dataNames: list):
        index = int(f'22{len(self.subplots)+1}')
        ax = self.fig.add_subplot(index)
        ax.set_xlim(self.t[0], self.maxPoints*self.dt)
        inits = [0]
        dataElements = {elem: inits for elem in dataNames}

        for elem, value in dataElements.items():
            ax.plot(self.t, value, label=elem)

        ax.set_xlim(self.t[0], self.maxPoints)
        ax.grid()
        ax.legend()

        self.data.update(dataElements)

        self.subplots.append(ax)
        

    def run(self):
        ani = animation.FuncAnimation(self.fig,
                                      self.anim,
                                      interval=100,
                                      cache_frame_data=False)
        
        plt.show()

    def anim(self, *args):
        while not self.q.empty():
            self.addData(self.q.get())

        for ax in self.subplots:
            ylim = ax.get_ylim()
            if len(self.t) >= self.maxPoints: ax.set_xlim(self.t[0], self.t[-1])
            for line in ax.get_lines():
                lineData = line.get_ydata()
                if min(lineData) < ylim[0]:
                    ax.set_ylim(min(lineData), ylim[1])
                if max(lineData) > ylim[1]:
                    ax.set_ylim(ylim[0], max(lineData))
                line.set_data(self.t, self.data[line.get_label()])

        

    def addData(self, data: dict):
        
        size = len(data[list(data)[-1]])
        
        for _ in range(size): self.t.append(self.t[-1]+self.dt)
        if len(self.t) > self.maxPoints: self.t = self.t[size:]

        for elem, value in data.items():
            self.data[elem] = self.data[elem] + value
            if len(self.data[elem]) > self.maxPoints:
                self.data[elem] = self.data[elem][size:]

    def cleanup(self):
        self.running = False
        print('wow')

tings = ['s', 'k']
tings2 = ['x', 'y', 'z']
tings3 = ['a', 'b']

queue = Queue()
app = Grapher(1, queue)

app.addSubplot(tings)
app.addSubplot(tings2)
app.addSubplot(tings3)


def main():
    for _ in range(10):
        startTime = time()


        sampleSize = randint(1, 1)
        uptDict = {
            's': [randint(-100, 100)]*sampleSize,
            'k': [randint(-120, 80)]*sampleSize,
            'x': [randint(-100, 600)]*sampleSize,
            'y': [randint(-50, 130)]*sampleSize,
            'z': [randint(-120, 120)]*sampleSize,
            'a': [randint(-60, 60)]*sampleSize,
            'b': [randint(-40, 80)]*sampleSize,
        }
        queue.put(uptDict)


        elapsedTime = (time() - startTime)*1000
        print(f'Elapsed time: {elapsedTime:0.2f}ms')
        sleep(0.1)

if __name__ == '__main__':
    app.start()
    main()
    app.cleanup()
    app.join()