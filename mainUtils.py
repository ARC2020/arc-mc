from modules.arc_mc_ui.XboxCtrl import XboxCtrl
from modules.arc_mc_components.throttle import Throttle
from modules.arc_mc_components.stepper import Stepper
from modules.arc_mc_components.ebrake import Ebrake
from modules.arc_mc_components.tachometer import Tachometer
from modules.arc_mc_components.rpi_interface import IO
from modules.arc_mc_ctrlsys.interfaces import Steering, Speed

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
        self.manualController = XboxCtrl(simulationMode)
        self.gpioPeripheralSetup(gpioFileName)
        
    def gpioPeripheralSetup(self, fileName = None):
        if fileName is None:
            fileName = self.gpioFileName
        with open(fileName) as f:
            data = load(f)
            pinThrottle = data["throttle"]
            pinStepDir = data["stepperDir"]
            pinStepPul = data["stepperPul"]
            pinMBrake = data["mBrake"]
            pinEBrake = data["eBrake"]
            pinTachBtn = data["tachometerButton"]
            pinTachSense = data["tachometerSense"]
            pinTachPwr = data["tachometerPower"]

        self.gpio = IO()
        self.throttle = Throttle(self.gpio, pin = pinThrottle, pwm = 0)
        self.throttle.setup()
        self.stepper = Stepper(self.gpio, pinDir = pinStepDir, pinPul = pinStepPul)
        self.stepper.setup()
        self.ebrake = Ebrake(self.gpio, pinMBrake, pinEBrake)
        self.ebrake.setup()
        self.tachometer = Tachometer(self.gpio, pinTachSense, pinTachBtn, pinTachPwr)
        self.tachometer.setup()

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

    def autoDrive(self):
        # TODO autoDrive code
        pass

    def deinit(self):
        self.ebrake.setEbrake(state = 0)
        self.throttle.off()
        self.stepper.reset()
        self.tachometer.off() # TODO double-check this
        self.gpio.disconnect()
        self.manualController.deinit()
