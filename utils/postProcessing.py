import pickle
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class PostProcessing():
    def __init__(self, voltsFileName = 'voltsList.pickle', anglesFileName = 'anglesList.pickle', framesFileName = 'framesList.pickle', speedsFileName = 'speedsList.pickle'):
        self.voltsList = self.unpickle(voltsFileName)
        self.anglesList = self.unpickle(anglesFileName)
        self.framesList = self.unpickle(framesFileName)
        self.speedsList = self.unpickle(speedsFileName)
        self.max = min(len(self.voltsList), len(self.anglesList))
        self.counter = 0
        self.fig = None
        self.voltAxes = None
        self.angleAxes = None
        self.framesAxes = None
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
        writer = writer(fps=100, metadata=dict(artist='ARC'), bitrate = 1800)
        self.ani.save(saveAs, dpi=100)
    
    def animate(self,interval):
        if self.counter == self.max: # no more data
            self.ani.event_source.stop()
            return
           
        self.angleAxes.clear()
        self.voltAxes.clear()
        self.framesAxes.clear()

        self.angleAxes.set_title('Steering Angle')
        self.angleAxes.set_theta_zero_location('N')
        self.angleAxes.set_xlim([-np.pi/4, np.pi/4])
        self.angleAxes.set_ylim([0, 2])
        self.angleAxes.set_yticklabels([])

        self.voltAxes.set_title('Throttle Voltage and Speed')
        self.voltAxes.set_ylabel('')
        self.voltAxes.set_xlabel('')
        self.voltAxes.set_xlim([0, 55])
        self.voltAxes.set_ylim([0, 4])
        self.voltAxes.grid(True)

        self.framesAxes.set_title('RealSense Camera Frame')
        self.framesAxes.axis('off')

        timeX = [i for i in range(0, self.counter)]
        voltY = self.voltsList[slice(self.counter)]
        speedY = self.speedsList[slice(self.counter)]
        angleX, angleY = self.calcXYfromAngle(self.anglesList[self.counter])

        self.angleAxes.quiver(0, 0, angleX, angleY, color = ['m'], scale = 2)
        self.voltAxes.plot(timeX, voltY, label = 'Throttle Voltage (V)')
        self.voltAxes.plot(timeX, speedY, label = 'Speed (m/s)')
        self.framesAxes.imshow(self.framesList[self.counter])

        self.voltAxes.legend()

        self.counter = self.counter + 1

    def calcXYfromAngle(self, angleDegree):
        if angleDegree > 45 or angleDegree < -45:
            angleDegree = 0
        angleRad = (angleDegree+90) * np.pi/180
        y = np.sin(angleRad)
        x = -np.cos(angleRad)
        return (x, y)
    
    def runAnimation(self, updateInterval, saveAs = 'animation.mp4'):
        self.fig = plt.figure(figsize=(15,10))
        self.angleAxes = self.fig.add_subplot(2,2,3, polar=True, projection='polar')
        self.voltAxes = self.fig.add_subplot(2,2,4)
        self.framesAxes = self.fig.add_subplot(2,1,1)

        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=updateInterval ,blit=False, repeat=False, frames = self.max)
        #either save it or show it - don't do both - results in recursion stack errors
        if saveAs != '':
            self.saveMP4(saveAs) 
        else:
            plt.get_current_fig_manager().window.state('zoomed')
            plt.show()


def testMain():
    import imageio
    numEntries = 90
    voltsFileName = 'voltsList.pickle'
    anglesFileName = 'anglesList.pickle'
    framesFileName = 'framesList.pickle'
    
    anglesList = [i for i in range(-45, 45)]
    voltsList = np.random.randint(low =0, high=3, size =numEntries)
    framesList = []
    for i in range(-45,45):
        if i%2 == 0:
            framesList.append(imageio.imread(r'\test2.png'))
        else:
            framesList.append(imageio.imread(r'\test.png'))

    try:
        with open(voltsFileName, 'wb') as pickleOut: #overwrites existing file
            pickle.dump(voltsList, pickleOut, pickle.HIGHEST_PROTOCOL)
        
        with open(anglesFileName, 'wb') as pickleOut:
            pickle.dump(anglesList, pickleOut, pickle.HIGHEST_PROTOCOL)

        with open(framesFileName, 'wb') as pickleOut:
            pickle.dump(framesList, pickleOut, pickle.HIGHEST_PROTOCOL)

    except pickle.PicklingError as e:
        print('An exception occured: ', e)

    obj = PostProcessing(voltsFileName, anglesFileName)
    obj.runAnimation(1000, '') #specify how frequently it should grab new data and update plots

def main():
    obj = PostProcessing()
    obj.runAnimation(280, 'animate5.mp4') #specify how frequently (in ms) it should grab new data and update plots

if __name__ == "__main__":
    main()
    #testMain()
    
