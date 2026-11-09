
from math import radians, sin, cos, pi, degrees
from time import time, sleep

class Odometer:

    # ============================================================
    # COLOR CONSTANTS
    # ============================================================

    BLACK_PERCENT = 0.19     # percent of the difference in color between the line and the board
    
    def __init__(self, robot, left_color_sensor, right_color_sensor):
        
        # Robot
        self.robot = robot

        # Sensors
        self.left_color_sensor = left_color_sensor
        self.right_color_sensor = right_color_sensor
        
        # Position
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.theta = 0.0

        # Take ground average
        self.ground_average = self._find_ground_color()

        # Downtime Flag for line detection
        self.line_downtime_flag = False
        self.line_downtime_flag_start = time()

        # Values need for the odometer calculations
        self.previous_left_encoder = self.robot.left_motor.get_encoder()
        self.previous_right_encoder = self.robot.right_motor.get_encoder()

    # ============================================================
    # ROBOT SENSOR FUNCTIONS
    # ============================================================

    def _over_black(self):
        right = self.right_color_sensor.get_rgb()
        left = self.left_color_sensor.get_rgb()
        
        ground_left, ground_right = self.ground_average

        # Removing Sensor Error
        if None in right:
            average_right = ground_right
        else:
            average_right = sum(right) / 3
        if None in left:
            average_left = ground_left
        else:
            average_left = sum(left) / 3
            

        return average_left < ground_left - ground_left*self.BLACK_PERCENT, average_right < ground_right - ground_right*self.BLACK_PERCENT
    def _find_ground_color(self):
        l, r = 0, 0
        for _ in range (20):
            r += sum(self.right_color_sensor.get_rgb()) / 3
            l +=  sum(self.left_color_sensor.get_rgb()) / 3
            sleep(0.1)
        return l / 20, r / 20
    
    # ============================================================
    # ODOMETER FUNCTIONS
    # ============================================================

    def convert_block_to_coordinates(self, block_number):
        return block_number * self.robot.SQUARE_DIM

    def _snap_float_to_nearest_multiple(self, value, multiple):
        if value % multiple > multiple/2: 
            return value + multiple - (value % multiple)
        else:
            return value - value % multiple

    def update_odometer(self):
        """
        Function to update the odomotor (i.e. x_pos, y_pos, and theta), called by execute once every cycle. 

        The first part updates the physical position by calculating distance traved using arc length of the wheel, and then the change
        in angle using a small angle approx.
        """
        L = self.robot.left_motor.get_encoder()
        R = self.robot.right_motor.get_encoder()
        # angle * radius = arc length
        dL = radians(L - self.previous_left_encoder) * self.robot.WHEEL_RADIUS
        dR = radians(R - self.previous_right_encoder) * self.robot.WHEEL_RADIUS
        self.previous_left_encoder, self.previous_right_encoder = L, R
        d = (dL + dR) / 2 # Distance Traveled (average)
        # Using dL-dR as opposite side of triangle, TRACK_WIDTH as hypotonous, and small angle aprox for sin dtheta = opp/hyp:
        dtheta = (dL - dR) / self.robot.TRACK_WIDTH      # left fwd + right back -> theta increases
        self.x_pos += d * sin(radians(self.theta) + dtheta / 2)
        self.y_pos += d * cos(radians(self.theta) + dtheta / 2)
        self.theta = (self.theta + degrees(dtheta)) % 360.0
        print(f"Current x: {self.x_pos:.2f}, Current y: {self.y_pos:.2f}, Current theta: {self.theta:.2f}")

    def correct_odometer(self):
        if self.line_update:
            left_over, right_over = self._over_black()
            if (left_over or right_over) and not self.line_downtime_flag:
                # One sensor on line other off, shift till both on top
                if right_over:
                    self.robot.pivot_right()
                else:
                    self.robot.pivot_left()
                while not (left_over and right_over) and not (not left_over and not right_over):
                        # Terminates either when both or over or neither are over (incase of over correction)
                        left_over, right_over = self._over_black()
                        self.update_odometer()
                        sleep(self.robot.LOOP_DOWNTIME)

                # If a line was hit, wait till it was crossed before detecting a new one
                # This flag doesn't trigger in the case the loop terminated when both the sensors suddenly saw no black
                self.line_downtime_flag = True
                self.line_downtime_flag_start = time()

                # Return the robot to moving straight 
                self.straight()
                # Both sensors over black line, snap to 90 degrees, update position:

                # Snapping Angle:
                self.theta = self._snap_float_to_nearest_multiple(self.theta, 90.0)
                self.theta = self.theta % 360.0
                
                # Update position
                if self.theta == 0:
                    # Facing North
                    self.y_pos = self._snap_float_to_nearest_multiple(self.y_pos, self.robot.SQUARE_DIM)
                    self.y_pos -= self.robot.DISTANCE_TO_CENTER # Adjusting for the fact that the sensor is infront of body
                elif self.theta == 90:
                    # Facing East
                    self.x_pos = self._snap_float_to_nearest_multiple(self.x_pos, self.robot.SQUARE_DIM)
                    self.x_pos -= self.robot.DISTANCE_TO_CENTER # Adjusting for the fact that the sensor is infront of body
                elif self.theta == 180:
                    # Facing South
                    self.y_pos = self._snap_float_to_nearest_multiple(self.y_pos, self.robot.SQUARE_DIM)
                    self.y_pos += self.robot.DISTANCE_TO_CENTER # Adjusting for the fact that the sensor is infront of body
                elif self.theta == 270:
                    # Facing West
                    self.x_pos = self._snap_float_to_nearest_multiple(self.x_pos, self.robot.SQUARE_DIM)
                    self.x_pos += self.robot.DISTANCE_TO_CENTER # Adjusting for the fact that the sensor is infront of body
                else:
                    # The position isn't snapping correctly
                    print(f"Currently facing: {self.theta}")
                
            else:
                # handling a downtime flag: saw a black line, so wait until completely off before we can detect a new one
                if abs(time() - self.line_downtime_flag_start) > 1.0 and self.line_downtime_flag:
                    self.line_downtime_flag = False
    
