simMode = False

from modules.arc_mc_ui.AppARC import AppARC
from time import sleep
from mainUtils import MainUtils

###################
# Initialization
###################

# GUI Initialization - spawn the UI thread and display the loading screen
gui = AppARC()
gui.start()

# Peripheral initialization
mainUtils = MainUtils(simMode)          
    # TODO figure out how behaviour for gpio peripherals would differ in simMode
    # includes throttle, stepper, ebrake and tachometer gpio setup
    # includes manual controller setup - set simMode to true if controller is not connected


# Socket initialization
# TODO on socket event, display images on GUI - call gui.display_image(file_path)
# TODO socket stuff for depth and pathWidth data


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
        mainUtils.autoDrive()
        # TODO if obstacle detected, display prompt using:
        # response = gui.show_yesno_prompt('Obstacle Detected', 'Would you like to switch to manual mode?')
        # if response:
        #     gui.toggle_mode(False) #False sets it to manual_mode, True sets it to auto_mode
        # ----OR----
        # gui.show_info_prompt('Obstacle Detected', 'Click ok to switch to manual mode.') 
        # gui.toggle_mode(False) #False sets it to manual_mode, True sets it to auto_mode
        print('in auto loop')
    else:  # manual mode
        if not mainUtils.manualController.is_connected():
            mainUtils.manualController.reconnect()
            print('trying to connect to controller')
            sleep(1)
            continue

        if mainUtils.manualController.check_brake() == 0 and mainUtils.ebrake.flagBrake == 0:
            mainUtils.manualDrive()
            print('in manual loop')
    
    #display speed on gui
    gui.display_speed(mainUtils.tachometer.speed)


###################
# Deinitialize
###################
mainUtils.deinit()
# not necessary to call gui.deinit() here because that is what triggers the drive loop to end

##############
