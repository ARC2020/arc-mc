import pickle
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class PostProcessing():
    def __init__(self, speedsFileName = 'speedsList.pickle', anglesFileName = 'anglesList.pickle'):
        self.speedsList = self.unpickle(speedsFileName)
        self.anglesList = self.unpickle(anglesFileName)
        self.max = min(len(self.speedsList), len(self.anglesList))
        self.counter = 0
        self.fig = None
        self.speedAxes = None
        self.angleAxes = None
        self.ani = None
        plt.rcParams['animation.ffmpeg_path'] = '/ffmpeg-4.2.2-win64-static/bin/ffmpeg.exe'

    def unpickle(self, fileName):
        try:
            with open(fileName, 'rb') as pickleIn:
                return pickle.load(pickleIn)
        except pickle.UnpicklingError as e:
            print('An exception occured: ', e)
    
    def saveMP4(self, saveAs):
        writer = animation.writers['ffmpeg']
        writer = writer(fps=30, metadata=dict(artist='ARC'), bitrate = 1800)
        self.ani.save(saveAs)
    
    def animate(self,interval):
        if self.counter == self.max-1: # no more data
            self.ani.event_source.stop()
            return
           
        self.angleAxes.clear()
        self.speedAxes.clear()

        self.angleAxes.set_title('Steering Angle')
        self.angleAxes.set_theta_zero_location('N')
        self.angleAxes.set_xlim([-np.pi/4, np.pi/4])
        self.angleAxes.set_ylim([0, 2])
        self.angleAxes.set_yticklabels([])

        self.speedAxes.set_title('Bike Speed')
        self.speedAxes.set_ylabel('Speed (m/s)')
        self.speedAxes.set_xlabel('Some Increment')
        self.speedAxes.set_xlim([0, 300])
        self.speedAxes.set_ylim([0, 10])
        self.speedAxes.grid(True)

        timeX = [i for i in range(0, self.counter)]
        speedY = self.speedsList[slice(self.counter)]
        angleX, angleY = self.calcXYfromAngle(self.anglesList[self.counter])

        self.angleAxes.quiver(0, 0, angleX, angleY, color = ['m'], scale = 2)
        self.speedAxes.plot(timeX, speedY)

        self.counter = self.counter + 1

    def calcXYfromAngle(self, angleDegree):
        angleRad = (angleDegree+90) * np.pi/180
        y = np.sin(angleRad)
        x = np.cos(angleRad)
        return (x, y)
    
    def runAnimation(self, updateInterval, saveAs = 'animation.mp4'):
        self.fig = plt.figure()
        self.angleAxes = self.fig.add_subplot(2,1,1, polar=True, projection='polar')
        self.speedAxes = self.fig.add_subplot(2,1,2)

        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=updateInterval ,blit=False, repeat=False, frames = self.max-1)
        #either save it or show it - don't do both - results in recursion stack errors
        if saveAs != '':
            self.saveMP4(saveAs) 
        else:
            plt.show()

if __name__ == "__main__":
    numEntries = 90
    speedsFileName = 'speedsList.pickle'
    anglesFileName = 'anglesList.pickle'
    
    anglesList = [i for i in range(-45, 45)]
    speedsList = np.random.randint(low =0, high=7, size =numEntries)
    
    try:
        with open(speedsFileName, 'wb') as pickleOut: #overwrites existing file
            pickle.dump(speedsList, pickleOut, pickle.HIGHEST_PROTOCOL)
        
        with open(anglesFileName, 'wb') as pickleOut:
            pickle.dump(anglesList, pickleOut, pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError as e:
        print('An exception occured: ', e)

    obj = PostProcessing(speedsFileName, anglesFileName)
    obj.runAnimation(500, '') #specify how frequently it should grab new data and update plots
    
