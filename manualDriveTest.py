from modules.arc_mc_ui.XboxCtrl import XboxCtrl
from modules.arc_mc_components.throttle import Throttle
from modules.arc_mc_components.stepper import Stepper
from modules.arc_mc_components.rpi_interface import IO
from modules.arc_mc_ctrlsys.interfaces import Steering, Speed

from time import sleep


def main():
    controller = XboxCtrl()
    gpio = IO()
    throttle = Throttle(gpio, pin = 4, pwm = 0)
    throttle.setup()
    stepper = Stepper(gpio, pinDir = 17, pinPul = 27)
    stepper.setup()
    
    while(1):
        sleep(0.5)
        if not controller.is_connected():
            controller.reconnect()
            print('reconnecting to controller')
            sleep(1)
        elif controller.check_brake() == 0:
            # read controller.get_throttle_position() and write to throttle GPIO pin
            throttlePos = controller.get_throttle_position()
            throttleVoltage = Speed.joystickToThrottle(throttlePos)
            throttle.setVolt(throttleVoltage)
            print(f"throttlePos: {throttlePos}, throttleVolt: {throttleVoltage}")
            # read controller.get_steering_position() and write to stepper GPIO pin
            steeringPos = controller.get_steering_position()
            steeringAngle = Steering.joystickToSteeringAngle(steeringPos)
            #stepper.rotate(steeringAngle)
            print(f"steeringPos: {steeringPos}, steeringAngle: {steeringAngle}")
        else:
            print("Brake condition ",controller.check_brake())
            print("Brake pressed, deiniting ...")
            controller.deinit()
            throttle.off()
            gpio.disconnect()
            break
            # TODO stepper deinit


if __name__ == "__main__":
    main()
