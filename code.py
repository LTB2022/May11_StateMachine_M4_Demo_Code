# State Classes rev 1
# rev 1 contains code state machine, RTC and SD card wrtiting

# pylint: disable=global-statement,stop-iteration-return,no-self-use,useless-super-delegation

import time
import board
import  digitalio
from adafruit_debouncer import Debouncer

import busio
import adafruit_pcf8523
import adafruit_register

import adafruit_sdcard
import storage


###############################################################################

# Set to false to disable testing/tracing code
TESTING = True

################################################################################
# Setup hardware

# Pins
SWITCH_1_PIN = board.D5
SWITCH_2_PIN = board.D6

# Lights up LED for log on SD card:
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

switch_1_io = digitalio.DigitalInOut(SWITCH_1_PIN)
switch_1_io.direction = digitalio.Direction.INPUT
switch_1_io.pull = digitalio.Pull.UP
switch_1 = Debouncer(switch_1_io)

switch_2_io = digitalio.DigitalInOut(SWITCH_2_PIN)
switch_2_io.direction = digitalio.Direction.INPUT
switch_2_io.pull = digitalio.Pull.UP
switch_2 = Debouncer(switch_2_io)

#################################################################################################
# Setting up the Real Time Clock and set the initial time

# Creates object I2C that connects the I2C module to pins SCL and SDA
myI2C = busio.I2C(board.SCL, board.SDA)
# Creates an object that can access the RTC and communicate that information along using I2C.
rtc = adafruit_pcf8523.PCF8523(myI2C)

if True:   # change to True if you want to write the time!
# Note this code is in a loop and will continue to use this statement
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    #   t is a time object
    t = time.struct_time((2022,  04,   05,   15,  43,  0,    0,   -1,    -1))

    #print("Setting time to:", t)     # uncomment for debugging
    rtc.datetime = t
    #print()

# Verifying the set time
# while True:
#    t = rtc.datetime
#    #print(t)     # uncomment for debugging

#    print("The date is %s %d/%d/%d" % (days[t.tm_wday], t.tm_mday, t.tm_mon, t.tm_year))
#    print("The time is %d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec))

#    time.sleep(1) # wait a second

##################################################################################################
#SD Card

# Creates object that connects SPI bus and a digital output for the microSD card's CS line.
# The pin name should match our wiring.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# This is the chip select line on the M4 board.
cs = digitalio.DigitalInOut(board.D10)

# This creates the microSD card object and the filesystem object:
# Inputs are the spi and cs objects.
sdcard = adafruit_sdcard.SDCard(spi, cs)
# The microSD card object and the filesystem object are now
# being passed through Vfsfat class.
vfs = storage.VfsFat(sdcard)

# We can now make the path /sd on the CircuitPython
# filesystem read and write from the card:
storage.mount(vfs, "/sd")

# Creates a file and writes name inside a text file along the path.
with open("/sd/stamp.csv", "a") as f:
    f.write("Date, Time In, Time Out , Total, Voice Note\r\n")
print("Logging column names into the filesystem")


################################################################################
# Global Variables
#NOTE THIS MAY NOT BE NEEDED, THESE VARIABLES ARE ONLY AVAILABLE TO THE LOOP, WHICH
#IS LOCATED OUTSIDE OF MACHINE STATES

# Variables for time stamps
# "date in" stamp
"""documentation version of "commenting out" """
""" global_month_in = month_in
global_day_in = day_in
global_year_in = year_in

# "time in" stamp
global_hour_in = hour_in
global_min_in = min_in
global_sec_in = sec_in

# "date out" stamp
global_month_out = month_out
global_day_out = day_out
global_year_out = year_out

# "time out" stamp
global_hour_out = hour_out
global_min_out = min_out
global_sec_out = sec_out """



################################################################################
# Support functions

# Code tracing feature
def log(s):
    """Print the argument if testing/tracing is enabled."""
    if TESTING:
        print(s)


################################################################################
# State Machine, Manages states

class StateMachine(object):

    def __init__(self):                             # Needed constructor
        self.state = None
        self.states = {}
        #Initialization of global variables which are inherited by child states in the following code
        self.month_in = 0
        self.day_in = 0
        self.year_in = 0
        self.hour_in = 0
        self.min_in = 0
        self.sec_in = 0

        self.month_out = 0
        self.day_out = 0
        self.year_out = 0
        self.hour_out = 0
        self.min_out = 0
        self.sec_out = 0



    def add_state(self, state):                     # "add state" attribute, adds states to the machine
        self.states[state.name] = state

    def go_to_state(self, state_name):              # "go to state" attribute, facilittes transition to other states. Prints confirmation when "Testing = True"
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.enter(self)

    def pressed(self):                              # "button pressed" attribute. Accessed at the end of each loop, applies a pause and prints confirmaiton if setup.
        if self.state:
            log('Updating %s' % (self.state.name))
            self.state.pressed(self)
            #print("'StateMachine' Class occurrence")  # Use this print statement to understand how the states transition here to update the state in the serial monitor
            time.sleep(.5)                             # Critial pause needed to prevent the serial monitor from being "flooded" with data and crashing



################################################################################
# States

# Abstract parent state class: I'm not 100% sure that this state is the "parent class" for the states below.
# So far "StateMachine" appears to be the parent class, some clarification is needed to indentify how a class is called by "super().__init__()" (aka "Inheritance")

class State(object):

    def __init__(self):         # Constructor. Sets variables for the class, in this instance only, "self". Note machine variable below in the "enter" attribute
        pass

    @property
    def name(self):             # Attribute. Only the name is returned in states below. The State object shouldn't be called and returns nothing
        return ''

    def enter(self, machine):   # Class Attribute. Does what is commanded when the state is entered
        pass

    def exit(self, machine):    # Class Attribute. Does what is commanded when exiting the state
        pass

    def pressed(self, machine): # Class Attribute. Does what is commanded when a button is pressed
        print("'State' Class occurrence")   #This hasn't been called yet, I used this as a test to investigate the "inheritance" of child classes below.

########################################
# This state is active when powered on and other states return here
class Home(State):

    def __init__(self):
        super().__init__()          # Child class inheritance

    @property
    def name(self):
        return 'Home'

    def enter(self, machine):
        State.enter(self, machine)
        # Display a screen for the "Home" State, or enable a pin that displays the "Home" screen
        print('#### Home State ####')
        print('Placeholder to display the home screen on Epaper')
        print('Placeholder to display date and time\n')

    def exit(self, machine):
        State.exit(self, machine)

    def pressed(self, machine):
        if switch_1.fell:                                         #
            machine.go_to_state('Profile 1')
        if switch_2.fell:
            machine.go_to_state('Profile 2')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Profile 1" state. Either choose to track a task or use a focus timer.
class Profile1(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Profile 1'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Profile 1 State ####')
        print('Placeholder to display Profile 1 Screen')
        print('Placeholder to display date and time\n')

    def exit(self, machine):
        State.exit(self, machine)


    def pressed(self, machine):
        if switch_1.fell:
            machine.go_to_state('Tracking1')
        if switch_2.fell:
            machine.go_to_state('Focus Timer 1')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Tracking 1" state. Begin tracking task 1 in this state
class Tracking1(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Tracking1'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Tracking Task 1 State ####')
        print('Placeholder to display Tracking Task 1 Screen')
        print('Placeholder to display date and time')
        print('Placeholder to display counter for tracked time')

        print('Store a time-stamp for a tracking start time (global variable)\n')
        # This code is in process to store a "time in" stamp
        t = rtc.datetime

        # Components of the "time in" stamp
        self.month_in = t.tm_mon
        self.day_in = t.tm_mday
        self.year_in = t.tm_year

        # Components of the "time in" stamp
        self.hour_in = t.tm_hour
        self.min_in = t.tm_min
        self.sec_in = t.tm_sec
        print('Date in: ' + str(self.month_in) + '/' + str(self.day_in) + '/' + str(self.year_in) + '\n')
        print('Time in: ' + str(self.hour_in) + ':' + str(self.min_in) + ':' + str(self.sec_in) + '\n')


    def exit(self, machine):
        State.exit(self, machine)
        # Experiment clearing the Epaper Screen in this 'exit' attribute

    def pressed(self, machine):
        if switch_1.fell:                                         #Insert a switch #2 case, pull high or low to disable
            machine.go_to_state('Voice Note')
            print('Placeholder to store a time-stamp for a tracking END time (global variable)\n')

########################################
# The "Focus Timer 1" state. Begin the focus timer here
class FocusTimer1(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Focus Timer 1'


    def enter(self, machine):
        State.enter(self, machine)
        print('#### Focus Timer 1 State ####')
        print('Placeholder to display Focus Timer 1 Screen')
        print('Display Focus Timer counting down')
        print('Display date and time\n')
        # Display a screen for "Focus Timer 1" state, or enable a pin that displays the "Focus Timer 1" screen

    def exit(self, machine):
        State.exit(self, machine)


    def pressed(self, machine):
        if switch_1.fell:                   # Either button press results in a transition to the "Home" state
            machine.go_to_state('Home')
        if switch_2.fell:                   # Question: Perhaps a transition to "Profile1" is more appropriate?
            machine.go_to_state('Home')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Profile 2" state. Implement at a later date. Any button press in this state causes a transition to the "Home" state.
class Profile2(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Profile 2'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Profile 2 State ####')
        print('Placeholder to display Profile 2 Screen')
        print('Placeholder to display Profile 2 Screen, date and time\n')

    def exit(self, machine):
        State.exit(self, machine)


    def pressed(self, machine):
        if switch_1.fell:
            machine.go_to_state('Home')     # Either button press returns to "Home" state, further profiles will be implemented in the future
        if switch_2.fell:
            machine.go_to_state('Home')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Voice Note" state. A placeholder state that has an option to record a voice note or return to the "home" state
class VoiceNote(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Voice Note'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Voice Note State ####')
        print('Placeholder to display Voice Note Screen')
        print('Placeholder to display, "Yes or No" to record a note\n')

        print('Store a time-stamp to end tracking time (global variable)\n')
        # This code is in process to store a "time out" stamp
        t = rtc.datetime

        # Components of the "time out" stamp
        self.month_out = t.tm_mon
        self.day_out = t.tm_mday
        self.year_out = t.tm_year

        # Components of the "time out" stamp
        self.hour_out = t.tm_hour
        self.min_out = t.tm_min
        self.sec_out = t.tm_sec
        print("Date out: " + str(self.month_out) + "/" + str(self.day_out) + "/" + str(self.year_out) + '\n')
        print("Time out: " + str(self.hour_out) + ":" + str(self.min_out) + ":" + str(self.sec_out) + '\n')


    def exit(self, machine):
        State.exit(self, machine)


    def pressed(self, machine):
        if switch_1.fell:                   # Yes button results in a transition to the "Record" state
            machine.go_to_state('Record')
        if switch_2.fell:                   # No button results in a transition to the "Home" state
            machine.go_to_state('Home')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Record Note" state. A placeholder state that will record a note then transition to the "home" state
# Constains an easter egg photo of Professor Levine on vacation
class Record(State):

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Record'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Record Note State ####')
        print('Placeholder to display Prof. Levine on vacation Screen')                       # Easter egg
        print('Placeholder to display, "Placeholder for second semester functionality!"\n')

    def exit(self, machine):
        State.exit(self, machine)
        print('Log date, start time stamp, end time stamp and voice note to .csv\n')    # Upon exit, log the global variables containing time stamps to the SD Card
        print("Logging timestamp into filesystem")

        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/sd/stamp.csv", "a") as f:
            led.value = True
            t = rtc.datetime    #QUESTION: Do I need this in each class it is called?

            f.write("%d/%d/%d, " % (self.month_in, self.day_in, self.year_in))    # Common U.S. date format
            f.write("%d:%02d:%02d, " % (self.hour_in, self.min_in, self.sec_in))  # "Time in" written to file
            f.write("%d:%02d:%02d, " % (self.hour_out, self.min_out, self.sec_out))   #"Time-out" written to file

            delta_hour = self.hour_out - self.hour_in # Calculate hour difference
            delta_min = self.min_out - self.min_in  # Calculate min difference
            delta_sec = self.sec_out - self.sec_in # Calculate sec difference
            f.write("%d:%02d:%02d, " % (delta_hour, delta_min, delta_sec))  # Write the change in time to the file
            f.write("Speech to text voice note\r\n")
            f.write(None, None, None, "sum(d:d)\r\n",None)    #THERE IS PROBABLY AN ERROR HERE, In Excel you can't really sum items separated by ":"
            led.value = False  # turn off LED to indicate we're done

        # Read out all lines in the .csv file to verify the last entry
        #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

    def pressed(self, machine):

        if switch_1.fell:
            print('Placeholder to display "Ah Ah Ah" screen\n')                             # Easter egg
            machine.go_to_state('Home')                                                     # Return "Home"
        if switch_2.fell:
            print('Placeholder to display "Ah Ah Ah" screen\n')
            machine.go_to_state('Home')                                                     # Return "Home"



################################################################################
# Create the state machine

LTB_state_machine = StateMachine()          # Defines the state machine
LTB_state_machine.add_state(Home())         # Adds the listed states to the machine (Except for the class, "State"
LTB_state_machine.add_state(Profile1())
LTB_state_machine.add_state(Tracking1())
LTB_state_machine.add_state(FocusTimer1())
LTB_state_machine.add_state(Profile2())
LTB_state_machine.add_state(VoiceNote())
LTB_state_machine.add_state(Record())

LTB_state_machine.go_to_state('Home')   #Starts the state machine in the "Home" state

while True:
    switch_1.update()               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    switch_2.update()               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    LTB_state_machine.pressed()     #Transitions to the StateMachine attrubute, "pressed". Doesn't do much there other than report the current state
