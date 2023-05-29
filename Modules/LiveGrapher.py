import matplotlib.pyplot as plt

class Grapher:

    def __init__(self, dt: float):
        self.dt = dt
        self.t = [0]
        
        self.maxPoints = 100
        self.fig = plt.figure()
        self.subplots = []

        plt.ion()
        plt.show()

    def addSubplot(self, dataNames: list, initVals=None):
        index = int(f'22{len(self.subplots)+1}')
        ax = self.fig.add_subplot(index)
        inits = [0]*len(dataNames) if not initVals else initVals
        dataElements = {elem: [inits[i]] for i, elem in enumerate(dataNames)}
        graphElements = {}
        for elem, value in dataElements.items():
            graphElements[elem] = ax.plot(self.t, value, label=elem)
        newSub = {
            'ax': ax,
            'dataElements': dataElements,
            'graphElements': graphElements,
        }
        ax.grid()
        self.subplots.append(newSub)

    def update(self, data: dict):

        currentSubplot = 0
        i = 0
        for elem, value in data.items():
            if i == len(self.subplots[currentSubplot]['dataElements']):
                i = 0
                currentSubplot += 1
            
            self.subplots[currentSubplot]['dataElements'][elem].append(value)
            i+=1

        self.t.append(self.t[-1]+self.dt)
        if len(self.t) > self.maxPoints: self.t.pop(0)

        for subplot in self.subplots:
            for elem, value in subplot['dataElements'].items():
                if len(value) > self.maxPoints: value.pop(0)
                color = subplot['graphElements'][elem][0].get_color()
                subplot['graphElements'][elem][0].remove()
                subplot['graphElements'][elem] = subplot['ax'].plot(
                    self.t, value, label=elem, color=color)
            subplot['ax'].set_xlim(self.t[0], self.t[-1])
            subplot['ax'].legend()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

tings = ['s', 'k']
tings2 = ['x', 'y', 'z']
app = Grapher(1)
app.addSubplot(tings)
app.addSubplot(tings2)

from time import sleep, time


for i in range(200):
    startTime = time()
    uptDict = {
        's': i,
        'k': i**2,
        'x': i/(i+1),
        'y': i**(1/2),
        'z': 2*i,
    }
    app.update(uptDict)
    elapsedTime = (time() - startTime)*1000
    print(f'Elapsed time: {elapsedTime:0.2f}ms')
    sleep(0.1)

sleep(1000)