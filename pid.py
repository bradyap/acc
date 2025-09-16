import time


class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, min_dt=0.001):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain 
            kd: Derivative gain
            min_dt: Minimum time interval between updates
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_dt = min_dt

        self.prev_time = 0
        self.total_error = 0.0
        self.prev_error = 0.0

    def reset(self):
        self.prev_time = 0
        self.total_error = 0.0
        self.prev_error = 0.0

    def update(self, current_value, target_value):
        """
        Calculate PID output.

        Args:
            current_value: Current measured value
            target_value: Desired target value

        Returns:
            PID output correction value, or None if update skipped
        """
        current_time = time.time()
        dt = current_time - self.prev_time

        # Skip if dt is too small
        if dt < self.min_dt:
            return None

        # Update prev time
        self.prev_time = current_time

        # Handle bad readings
        if current_value == 0:
            return None

        error = target_value - current_value
        proportional = self.kp * error * dt

        # Integral term
        self.total_error += error
        integral = self.ki * self.total_error

        # Derivative term
        derivative = self.kd * (error - self.prev_error) / dt
        self.prev_error = error

        # Combine all terms
        correction = proportional + integral + derivative

        return correction