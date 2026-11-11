from utils.brick import Motor, EV3ColorSensor, NXTColorSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick
from time import sleep
from odometer import Odometer
from map import Map

class FinalRobot:
    
    # ============================================================
    # ROBOT PHYSICAL CONSTANTS
    # ============================================================

    WHEEL_RADIUS = 2.0        # cm, the radius of the wheels, used to calculate distance traveled
    TRACK_WIDTH = 15.5        # cm, the distance between the centers of the wheels, used to calculate delta theta
    DISTANCE_TO_CENTER  = 4   # cm, the distance from the sensors to the center of the robot

    SQUARE_DIM = 30.48        # cm, the length of the side of the square

    # ============================================================
    # ROBOT CODE CONSTANTS
    # ============================================================

    SPEED = 90.0              # degrees per second, standard speed for the robot
    LOOP_DOWNTIME = 0.01      # seconds, the time the robot pauses in between cycles
    POINT_TARGET_ERROR = 5    # cm
    



    def __init__(self, left_motor_id, right_motor_id, conveyer_motor_id, storage_motor_id, left_color_sensor_id, right_color_sensor_id, ultrasonic_sensor_id):
        """
        Instantiates the robot, taking the port ids to connect to the sensors and motors, waits until sensors are ready to exit

        Args:
            left_motor_id (str): the port ID of the left motor
            right_motor_id (str): the port ID of the right motor
            conveyer_motor_id (str): the port ID of the conveyer belt motor
            storage_motor_id (str): the port ID of the storage emptying motor
            left_color_sensor_id (int: the port ID of the left color sensor -- Should be EV3Color
            right_color_sensor_id (int): the port ID of the right color sensor -- Should be NXTColor
            ultrasonic_sensor_id (int): the port ID of the ultrasonic sensor
        """

        # Motors
        self.left_motor = Motor(left_motor_id)
        self.right_motor = Motor(right_motor_id)
        self.conveyer_motor = Motor(conveyer_motor_id)
        self.storage_motor = Motor(storage_motor_id)

        # Sensors
        self.left_color_sensor = EV3ColorSensor(left_color_sensor_id)
        self.right_color_sensor = NXTColorSensor(right_color_sensor_id)
        self.ultrasonic_sensor = EV3UltrasonicSensor(ultrasonic_sensor_id)

        # Setup
        wait_ready_sensors()

        # Odometer
        self.odometer = Odometer(self, self.left_color_sensor, self.right_color_sensor)

        # Mapping
        self.map = Map(self)


    # ============================================================
    # ODOMETER FUNCTIONS
    # ============================================================
    
    def x_pos(self):
        return self.odometer.x_pos
    
    def y_pos(self):
        return self.odometer.y_pos
    
    def update_odometer(self):
        self.odometer.update_odometer()

    def correct_odometer(self):
        self.odometer.correct_odometer()

    # ============================================================
    # ROBOT MOVEMENT FUNCTIONS
    # ============================================================

    def simple(self, left_speed, right_speed):
        """Simple function to update wheel speeds"""
        self.right_motor.set_dps(right_speed)
        self.left_motor.set_dps(left_speed)

    def go_distance(self, distance):
        self.straight()
        curr_x, curr_y = self.x_pos(), self.y_pos()
        while ((curr_x-self.x_pos())**2 + (curr_y-self.y_pos())**2)**0.5 <= distance:
            self.update_odometer()
            self.correct_odometer()
            sleep(self.LOOP_DOWNTIME)
        self.simple(0,0)
            
    def straight(self):
        self.simple(self.SPEED, self.SPEED-1.5)

    
    def pivot_right(self):
        self.simple(self.SPEED/2, -self.SPEED/2)

    def pivot_left(self):
        self.simple(-self.SPEED/2, self.SPEED/2)

    def turn_right_angle(self, angle):
        """Turns right by a specific angle
        
        Args:
            angle (float): the angle to turn right by 

        """
        intial_theta = self.theta
        self.pivot_right()
        if intial_theta + angle > 360:
            # Incase the angle wraps back down to 0
            while (intial_theta + self.theta) % 360 < angle - (360-intial_theta):
                self.update_odometer()
                sleep(self.LOOP_DOWNTIME)
        else:
            while abs(intial_theta-self.theta) < angle:
                self.update_odometer()
                sleep(self.LOOP_DOWNTIME)
        self.simple(0,0)

    def turn_left_angle(self, angle):
        """Turns left by a specific angle
        
        Args:
            angle (float): the angle to turn left by 

        """
        intial_theta = self.theta
        self.pivot_left()
        if intial_theta - angle < 0:
            # Incase the angle wraps back up to 360 
            while 0.0 <= self.theta <= intial_theta or 360.0 - (angle-intial_theta) <= self.theta <= 360.0:
                self.update_odometer()
                sleep(self.LOOP_DOWNTIME)
        else:
            while abs(intial_theta-self.theta) < angle:
                self.update_odometer()
                sleep(self.LOOP_DOWNTIME)
        self.simple(0,0)
    
    def face_angle(self, angle):
        """Turns to face a specific angle
        
        Args:
            angle (float): the angle to turn to 

        """

        if self.theta < angle:
            self.turn_right_angle(abs(angle-self.theta))
        else:
            self.turn_left_angle(abs(angle-self.theta))

    def safest_to_point(self, target_x, target_y):
        print(target_x, target_y)        
        if abs(target_x - self.x_pos()) > self.POINT_TARGET_ERROR:
            if target_x > self.x_pos():
                self.face_angle(90)
                self.go_distance(target_x-self.x_pos())
            elif target_x < self.x_pos():
                self.face_angle(270)
                self.go_distance(self.x_pos()-target_x)
        if abs(target_y - self.y_pos()) > self.POINT_TARGET_ERROR:
            if target_y > self.y_pos():
                self.face_angle(0)
                self.go_distance(target_y-self.y_pos())
            elif target_y < self.y_pos():
                self.face_angle(180)
                self.go_distance(self.y_pos()-target_y)