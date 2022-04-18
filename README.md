# Base_StateMachine_RTC_SDcard
An integration of the State Machine, Real-time Clock, SD card datalogging and outputs to enable epaper screens on the M4 express running Arduino code.

This is Rev_5, which integrates all components to demonstrate a deployable prototype.

Remaining issues:

1. The M4 express running the Arduino code continously refreshes the screen due to the high signal present at the input.
we need to stop polling the pin after a signal is initially read as high. 

2. This working machine needs to be transferred to a Raspberry Pi. 
