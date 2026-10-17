from utils.brick import Motor, EV3ColorSensor, NXTColorSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick
from math import radians, sin, cos, pi
class Robot:

    # ============================================================
    # ROBOT PHYSICAL CONSTANTS
    # ============================================================

    WHEEL_RADIUS = 3.0        # cm, the radius of the wheels, used to calculate distance traveled
    TRACK_WIDTH = 10.0        # cm   -> adjust if angle is off


    def __init__(self, left_motor_id, right_motor_id, left_light_sensor_id = None, right_light_sensor_id = None, ultrasonic_sensor_id = None, left_sensor_of_type_EV3 = True, left_sensor_type = "EV3Color", right_sensor_type = "NXTColor"):
        """
        Instantiates the robot, taking the port ids to connect to the sensors and motors, waits until sensors are ready to exit

        Args:
            left_motor_id (str): the port ID of the left motor
            right_motor_id (str): the port ID of the right motor
            left_light_sensor_id (int | None): the port ID of the left light sensor, defaults to None
            right_light_sensor_id (int | None): : the port ID of the right light sensor, defaults to None
            ultrasonic_sensor_id (int | None): : the port ID of the ultrasonic sensor, defaults to None
            left_sensor_type (str) : the brand of the left color sensor, defaults to EV3Color
            right_sensor_type (str) : the brand of the left color sensor, defaults to NXTColor
        
        """
        self.left_motor = Motor(left_motor_id)
        self.right_motor = Motor(right_motor_id)
        self.ultrasonic_sensor = self.create_sensor(ultrasonic_sensor_id, "EV3Ultrasonic")
        self.left_color_sensor = self.create_sensor(left_light_sensor_id, left_sensor_type)
        self.right_color_sensor = self.create_sensor(right_light_sensor_id, right_sensor_type)
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.theta = 0.0


        # Always waits to return till sensors are online
        wait_ready_sensors()

    def execute(self, lab_code):
        """
        Function to execute an operation with the robot. Runs continously until a error is thrown, a goal TaskCompleted exception is raised, or a KeyBoardInterupt is passed.
        Will automatically update odometer details. 

        Args:
            lab_code (func): the lab code to execute
        """
        try:
            while True:
                self.update_odometer()
                lab_code()
        except KeyboardInterrupt:
            print("Manualluy Interupted")
        except self.TaskCompleted:
            print("Successfully completed goal, terminated")
        except Exception as e:
            print(e)
        finally:
            self.right_motor.set_dps(0)
            self.left_motor.set_dps(0)
            reset_brick()

    def update_odometer(self):
        """
        Function to update the odomotor (i.e. x_pos, y_pos, and theta), called by execute
        """
        L = self.left_motor.get_encoder()
        R = self.right_motor.get_encoder()
        dL = radians(L - prev_L) * self.WHEEL_RADIUS
        dR = radians(R - prev_R) * self.WHEEL_RADIUS
        prev_L, prev_R = L, R
        d = (dL + dR) / 2
        dtheta = (dL - dR) / self.TRACK_WIDTH      # left fwd + right back -> theta increases
        self.x_pos += d * sin(self.theta + dtheta / 2)
        self.y_pos += d * cos(self.theta + dtheta / 2)
        self.theta = (self.theta + dtheta) % (2 * pi)


    def create_sensor(id : int, stype : str):
        """
        Helper function for constructor

        Args:
            id (int): the sensor ID
            stype (str): the type of sensor, options EV3Color, NXTColor, EV3Ultrasonic

        """
        if id is None:
            return None
        if stype == "EV3Color":
            return EV3ColorSensor(id)
        elif stype == "NXTColor":
            return NXTColorSensor(id)
        elif stype == "EV3Ultrasonic":
            return EV3UltrasonicSensor(id)
        else:
            raise KeyError("Invalid Sensor Type")
        
    class TaskCompleted(Exception):
        """Raised when the lab code is meant to exit after successfully completing all objectives"""
        pass