from modules.arc_mc_components.throttle import Throttle
from modules.arc_mc_components.stepper import Stepper
from modules.arc_mc_components.ebrake import Ebrake
from modules.arc_mc_ctrlsys.interfaces import Steering, Speed, Blobs

try:
    from modules.arc_mc_ui.XboxCtrl import XboxCtrl
    from modules.arc_mc_components.rpi_interface import IO
    from modules.arc_mc_components.tachometer import Tachometer
    import numpy as np 
except:
    pass

from json import load
from time import sleep

class MainUtils():
    def __init__(self, simulationMode, gpioFileName = None):
        self.simMode = simulationMode
        self.gpioFileName = "gpio-pins.json"
        self.ebrake = None
        self.throttle = None
        self.stepper = None
        self.tachometer = None
        self.gpio = None
        self.reinitAutoDrive = True

    def connectPeripherals(self):
        self.manualController = XboxCtrl(self.simMode)
        self.gpioPeripheralSetup(self.gpioFileName)

    def gpioPeripheralSetup(self, fileName = None):
        data = self.loadJson(fileName)
        self.gpio = IO()
        self.throttle = Throttle(self.gpio, pin = data["throttle"], pwm = 0)
        self.throttle.setup()
        self.stepper = Stepper(self.gpio, pinDir = data["stepperDir"], pinPul = data["stepperPul"])
        self.stepper.setup()
        self.ebrake = Ebrake(self.gpio, data["mBrake"], data["eBrake"])
        self.ebrake.setup()
        self.tachometer = Tachometer(self.gpio, data["tachometerSense"], data["tachometerButton"], data["tachometerPower"])
        self.tachometer.setup()

    def loadJson(self, fileName = None):
        if fileName is None:
            fileName = self.gpioFileName
        with open(fileName) as f:
            data = load(f)
            return data
            
    def manualDrive(self):
        try:
            # read controller.get_throttle_position() and write to throttle GPIO pin
            throttlePos = self.manualController.get_throttle_position()
            throttleVoltage = Speed.joystickToThrottle(throttlePos)
            self.throttle.setVolt(throttleVoltage)
            # print(f"throttlePos: {throttlePos}, throttleVolt: {throttleVoltage}")

            # read controller.get_steering_position() and write to stepper GPIO pin
            steeringPos = self.manualController.get_steering_position()
            steeringAngle = int(Steering.joystickToSteeringAngle(steeringPos))
            self.stepper.rotate(steeringAngle)
            #print(f"steeringPos: {steeringPos}, steeringAngle: {steeringAngle}")
        except Exception as e:
            self.stepper.store()
            # print(e)

    def setupAutoDrive(self):
        self.ebrake.setEbrake(state = 0) # stop bike 
        self.blobsCtrlSys = Blobs(circ = 2.055, bikeHalfWidth = 100) # set bike half width in pixels
        self.speedCtrlSys = Speed(circ = 2.055)
        self.steerCtrlSys = Steering()
        self.steerCtrlSys.setup()
        self.speedCtrlSys.setup()
        self.reinitAutoDrive = False 

    def autoDrive(self):
        # peripherals already initialized if not simMode
        # initialize autoDrive if necessary
        if self.reinitAutoDrive:
            self.setupAutoDrive()
       
        success = 1

        # TODO get actual CV data (probably pass object as parameter) and make sure this is the new data types
        sizeRand = np.random.randint(0,20)
        blobXpos = np.random.randint(0, 800, size = sizeRand)
        blobWidths = np.random.randint(0, 200, size = sizeRand)
        blobDepths = np.random.uniform(3, 15, size = sizeRand)
        bikeSpeed = np.random.uniform(0.2,1)
        bikePosPx = np.random.randint(200,600)
        targetPosM = np.random.uniform(0,0.5)
        bikePosM = np.random.uniform(0,0.5)
        sleep(0.1)
        
        # update blobs
        self.blobsCtrlSys.update(xPos = blobXpos, widths = blobWidths, depths = blobDepths, bikePos = bikePosPx)
        crashTimes = self.blobsCtrlSys.checkCrash(bikeSpeed)
      
        if self.blobsCtrlSys.checkEmergencyStop(crashTimes):
            success = 0
        else: 
            # calculate steering angle and throttle voltage
            throttleVolt = self.speedCtrlSys.feedInput(bikeSpeed, crashTimes)
            steeringAngle = self.steerCtrlSys.feedInput(bikePosM, targetPosM, distanceTarget = 1)
            if not self.simMode: # apply outputs
                self.stepper.rotate(steeringAngle)
                self.throttle.setVolt(throttleVolt)

        #print(f"inputs: bikeSpeed {bikeSpeed}, bike pos {bikePosM}, target pos {targetPosM}, crashTimes {crashTimes}")
        #print(f"outputs: throttleVolt {throttleVolt}, steeringAngle {steeringAngle}")
        
        return success

    def deinit(self):
        self.ebrake.setEbrake(state = 0)
        self.throttle.off()
        self.stepper.reset()
        self.tachometer.off() 
        self.gpio.disconnect()
        self.manualController.deinit()
