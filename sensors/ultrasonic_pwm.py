import RPi.GPIO as GPIO
import time

class UltrasonicPWM:
    def __init__(self, trig_pin, echo_pin):
        """
        Initialize Ultrasonic Sensor (HC-SR04 / JSN-SR04T)
        trig_pin: GPIO pin connected to TRIG
        echo_pin: GPIO pin connected to ECHO
        """
        self.TRIG = trig_pin
        self.ECHO = echo_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, False)
        time.sleep(2)
        print(f"[INFO] Ultrasonic sensor initialized (TRIG={self.TRIG}, ECHO={self.ECHO})")

    def get_distance(self):
        """
        Measure distance in centimeters using the ultrasonic sensor.
        Returns:
            float: distance in centimeters or None if timeout/error.
        """
        # Send 10μs pulse to trigger
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        pulse_start = time.time()
        timeout_start = time.time()

        # Wait for ECHO to go HIGH
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > 0.05:
                return None  # Timeout

        # Wait for ECHO to go LOW
        pulse_end = time.time()
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
            if pulse_end - pulse_start > 0.05:
                return None  # Timeout

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # convert to cm (speed of sound)
        distance = round(distance, 1)
        return distance

    def cleanup(self):
        """Clean up GPIO pins when done"""
        GPIO.cleanup()
