from time import sleep
from traceback import print_exc
from utils.brick import reset_brick

class Map:
    
    MIN_DISTANCE_TO_WALL = 10.0 # cm

    def __init__(self, robot) -> None:
        self.robot = robot
        self.step_list = []

    
    def replay_map(self):
        for step in self.step_list:
            step()
        
    def _at_exit(self. x_exit, y_exit):
        return (((self.robot.x_pos() - self.x_exit) ** 2) + ((self.robot.y_pos() - self.y_exit) ** 2))**0.5 <= self.robot.POINT_TARGET_ERROR # Cm

    def map_street(self, x_exit, y_exit):
        """
        Assumes that the robot is facing the entrance into the street at the entrance
        """
        while not self._at_exit(x_exit, y_exit):
                # Move to center of the block
                self.robot.go_distance(self.robot.SQUARE_DIM/2)
                if self.robot.ultrasonic_sensor.distance() >= 100:
                    step = lambda: self.robot.turn_right_angle(90)
                elif self.robot.ultrasonic_sensor.distance() <= self.MIN_DISTANCE_TO_WALL:
                    step = lambda: self.robot.turn_left_angle(90)
                else:
                    step = lambda: self.robot.go_distance(self.robot.SQUARE_DIM)
                
                self.step_list.append(step)
                step()
                sleep(self.robot.LOOP_DOWNTIME)
        