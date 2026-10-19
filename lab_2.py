from robot import Robot
from math import pi

r = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)

def head():
    print("start")
def body():
    for i in range(4):    
        r.go_distance(90)
        r.turn_right_angle(90)
    raise r.TaskCompleted
r.execute(head, body)

