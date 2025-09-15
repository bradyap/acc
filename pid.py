import time

KP = 1
KI = 0
KD = 0

prev_time = 0  # Last time PID ran
total_error = 0.0  # Integral term
prev_error = 0.0  # Previous error for derivative term


def pid_follow(current_distance, target_distance, fwd_motor_speed):
    global prev_time, total_error, prev_error

    current_time = time.time()  # Current time in seconds
    dt = current_time - prev_time  # Time since last PID update in seconds

    # Skip if dt is too small, don't need super rapid updates
    if dt < 0.001:
        return None, None

    # Otherwise run and update prev time
    prev_time = current_time

    # Handle bad readings
    if current_distance == 0:
        return None, None

    error = target_distance - current_distance
    proportional = KP * error * dt  # Proportional term

    # Integral term
    # TODO: Add limits to prevent integral windup?
    total_error += error
    integral = KI * total_error

    # Derivative term
    derivative = KD * (error - prev_error) / dt
    prev_error = error  # Store current error for next iteration

    # Combine all terms to get the final correction
    correction = proportional + integral + derivative

    # Adjust motor speeds accordingly
    left_speed = fwd_motor_speed + correction
    right_speed = fwd_motor_speed - correction

    # TODO: Add limits to control correction speed

    return left_speed, right_speed
