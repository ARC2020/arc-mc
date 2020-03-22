from modules.arc_mc_ui.AppARC import AppARC
from modules.arc_mc_ui.XboxCtrl import XboxCtrl

# from modules.arc-mc-ctrlsys import interfaces, pid
# from modules.arc-mc-components import rpi-interface, stepper
from time import sleep

###################
# Start
###################


###################
# Initialization
###################

# GUI Initialization - spawn the UI thread and display the loading screen
gui = AppARC()
gui.start()

# Peripheral initialization
manual_controller = XboxCtrl()

# Socket initialization
# TODO on socket event, display images on GUI - call gui.display_image(file_path)


###################
# Calibration
###################


# after the init and calibrate states, call gui.raise_main_frame to close the loading screen
gui.raise_main_frame()

###################
# Drive Loop
###################

while gui.isAlive():
    # if user has not started the trike, continue looping
    if not gui.is_trike_started:
        print('waiting for trike to start')
        sleep(2)
        continue

    if gui.is_auto_mode:
        print('in auto loop')
    else:  # manual mode
        if not manual_controller.is_connected():
            manual_controller.reconnect()
            print('trying to connect to controller')
            sleep(1)
            continue

        if manual_controller.check_brake() == 0 or not gui.is_auto_mode:
            # TODO in the condition above, also check the pysical brake GPIO pin
            # TODO read manual_controller.get_throttle_position() and write to throttle GPIO pin
            # TODO read manual_controller.get_stepper_position() and write to stepper GPIO pin
            print('in manual loop')


###################
# Deinit
###################
manual_controller.deinit()
# not necessary to call gui.deinit() here because that is what triggers the drive loop to end

##############
