#  M4 StateMachine for LTB May 11 demo
An integration of the State Machine, Real-time Clock, SD card datalogging and outputs to enable epaper screens on the M4 express running Arduino code.

This is Rev_5, which integrates all components to demonstrate a deployable prototype.

Remaining issues:
1. There is strange behavior when the epaper screen refreshes at 180 seconds, the current screen is lost due to the interrupt looking for "rising" signal change.
2. -
