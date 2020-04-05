from modules.arc_mc_ui.AppARC import AppARC
from time import sleep
from mainUtils import MainUtils

###################
# Initialization
###################

simMode = True

# GUI Initialization - spawn the UI thread and display the loading screen
gui = AppARC()
gui.start()

# Peripheral initialization
mainUtils = MainUtils(simMode) 
if not simMode:
    mainUtils.connectPeripherals() # throttle, stepper, ebrake, tachometer and manual controller setup

# Socket initialization
# TODO on socket event, display images on GUI - call gui.display_image(file_path)
# TODO socket stuff for depth and pathWidth data

# if not simMode, at this point we would perform calibration

# after the init and calibrate states, call gui.raise_main_frame to close the loading screen
sleep(0.25) # this is necessary
gui.raise_main_frame()

###################
# Drive Loop
###################

while gui.is_alive():
    # if user has not started the trike, continue looping
    if not gui.is_trike_started:
        print('waiting for trike to start')
        sleep(2)
        continue

    if gui.is_auto_mode:
        success = mainUtils.autoDrive()
        if not success:
            gui.show_info_prompt('Obstacle Detected', 
                'An obstacle was detected. Please click OK to switch to manual drive mode.') 
            gui.toggle_mode(False) # False sets mode to manual, True sets mode to auto
            if not simMode:
                mainUtils.ebrake.setEbrake(state = 0)
            else:
                print ('ebrake applied')
        print('in auto loop')
       
    else:  # manual mode
        mainUtils.reinitAutoDrive = True
        if not simMode:
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
if not simMode:
    mainUtils.deinit()
# not necessary to call gui.deinit() here because that is what triggers the drive loop to end

##############
