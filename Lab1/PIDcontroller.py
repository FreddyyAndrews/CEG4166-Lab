def straight(leftWheelEncoder, rightWheelEncoder, timer):
    # The role of the controller is to cancel the error of the system that is defined by the
    leftEncoderCount.resetTicks()
    rightEncoderCount.resetTicks()
    targetIteration = 10  # Keep this value as 10, it is easier to perform the path
    leftSpeed = 1530  # Try to use a value around 100 higher than the leftSpeed to keep the left wheel stopped
    rightSpeed = 1177  # Try to use a value around 100 lower than the rightSpeed to keep the right wheel stopped
    leftSpeedVar = leftSpeed  # Max speed
    rightSpeedVar = rightSpeed  # Max speed
    leftPError = 0
    rightPError = 0
    leftSError = 0
    rightSError = 0
    target = 0  # Initialize your target value for number of ticks as 0
    KP = 15  # You can improve this value by testing
    # Always try values between 0 and 50
    KD = 0  # 5 #You can improve this value by testing
    KI = 3.75  # You can improve this value by testing
    # A good starting is KP divided by 4
    sampleTime = 0.4  # Keep this value as 0.4 seconds
    timeout = time.time() + timer
    i = 0  # Variable to count the number of iterations

    while time.time() < timeout:
        leftError = target - leftWheelEncoder.getTicks()
        rightError = target - rightWheelEncoder.getTicks()

        if (abs(leftError) > 1) or (i == 0):  # Use 1 as a threshold, and it needs to be True when i == 0 (at the initial loop)
            leftSpeed += (leftError * KP) + ((leftError - leftPError) * KD) + (leftSError * KI)
            leftSpeed = max(min(leftSpeedVar, leftSpeed), 1720)

        if (abs(rightError) > 1) or (i == 0):  # Use 1 as a threshold, and it needs to be True when i == 0 (at the initial loop)
            rightSpeed -= (rightError * KP) + ((rightError - rightPError) * KD) + (rightSError * KI)
            rightSpeed = min(max(rightSpeedVar, rightSpeed), 1280)

        Robot_forward(leftSpeed, rightSpeed)

        time.sleep(sampleTime)

        leftPError = leftError
        rightPError = rightError
        leftSError += leftError
        rightSError += rightError

        target += targetIteration  # Actualize your target by adding the targetIteration at the end of each iteration
        i += 1  # Actualize the number of iterations

    motorStop()
    # Robot_forward(1420+13*leftError, 1260-13*rightError)  # This is to compensate any errors when the robot stops
    # To compensate the final error, use the speed to keep the wheels stopped, and add or subtract the error
    # multiplied by a number. This number you need to find by testing.

    time.sleep(0.1)
    motorStop()
