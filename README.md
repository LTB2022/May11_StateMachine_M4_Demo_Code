# Base_StateMachine_RTC_SDcard
An integration of the State Machine, Real-time Clock and SD card datalogging

This is Rev_2. The time stamp and date stamps are recorded to the SD card but show "0" for all fields. The variables for date and time are intended to be global
and are therefore located in the parent "State" class. There is a bug where the child classes are not updated the variable value, this may requrire a "global" declaration in the "State" class.

The StateMachine "time.sleep" was changed from .5 seconds to 0.125 seconds, better response from the button is the result.
