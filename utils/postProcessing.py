import pickle
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class PostProcessing():
    def __init__(self, voltsFileName = 'voltsList.pickle', anglesFileName = 'anglesList.pickle', framesFileName = 'framesList.pickle'):
        self.voltsList = self.unpickle(voltsFileName)
        self.anglesList = self.unpickle(anglesFileName)
        self.framesList = self.unpickle(framesFileName)
        self.max = min(len(self.voltsList), len(self.anglesList))
        self.counter = 0
        self.fig = None
        self.voltAxes = None
        self.angleAxes = None
        self.framesAxes = None
        self.ani = None
        plt.rcParams['animation.ffmpeg_path'] = 'C:/Users/munif/Desktop/ffmpeg-4.2.2-win64-static/bin/ffmpeg.exe'

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
        self.voltAxes.clear()
        self.framesAxes.clear()

        self.angleAxes.set_title('Steering Angle')
        self.angleAxes.set_theta_zero_location('N')
        self.angleAxes.set_xlim([-np.pi/4, np.pi/4])
        self.angleAxes.set_ylim([0, 2])
        self.angleAxes.set_yticklabels([])

        self.voltAxes.set_title('Throttle Voltage')
        self.voltAxes.set_ylabel('Throttle Voltage (V)')
        self.voltAxes.set_xlabel('Some Increment??')
        self.voltAxes.set_xlim([0, 300])
        self.voltAxes.set_ylim([0, 2])
        self.voltAxes.grid(True)

        self.framesAxes.set_title('RealSense Camera Frame')
        self.framesAxes.axis('off')

        timeX = [i for i in range(0, self.counter)]
        voltY = self.voltsList[slice(self.counter)]
        angleX, angleY = self.calcXYfromAngle(self.anglesList[self.counter])

        self.angleAxes.quiver(0, 0, angleX, angleY, color = ['m'], scale = 2)
        self.voltAxes.plot(timeX, voltY)
        self.framesAxes.imshow(self.framesList[self.counter])

        self.counter = self.counter + 1

    def calcXYfromAngle(self, angleDegree):
        angleRad = (angleDegree+90) * np.pi/180
        y = np.sin(angleRad)
        x = -np.cos(angleRad)
        return (x, y)
    
    def runAnimation(self, updateInterval, saveAs = 'animation.mp4'):
        self.fig = plt.figure()
        self.angleAxes = self.fig.add_subplot(2,2,3, polar=True, projection='polar')
        self.voltAxes = self.fig.add_subplot(2,2,4)
        self.framesAxes = self.fig.add_subplot(2,1,1)
        #plt.subplots_adjust(hspace = 0.3)
        plt.get_current_fig_manager().window.state('zoomed')

        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=updateInterval ,blit=False, repeat=False, frames = self.max-1)
        #either save it or show it - don't do both - results in recursion stack errors
        if saveAs != '':
            self.saveMP4(saveAs) 
        else:
            plt.show()

if __name__ == "__main__":
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
            framesList.append(imageio.imread(r'C:\Users\munif\Desktop\test2.png'))
        else:
            framesList.append(imageio.imread(r'C:\Users\munif\Desktop\test.png'))

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
    obj.runAnimation(500, '') #specify how frequently it should grab new data and update plots
    
