from robot import Robot
from math import atan2, degrees
from time import sleep

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=1, right_light_sensor_id=3)

ERROR = 1

suzuki.x_pos = 0
suzuki.y_pos = 0

suzuki.line_update = False

way_points = []

for i in range (4):
    x = int(input(f"X coordinate {i+1}: "))
    y = int(input(f"Y coordinate {i+1}: "))
    way_points.append((x, y))


def angle_difference(target, current):
    return ((target - current + 180.0) % 360.0) - 180.0

def turn_to(angle):
    suzuki.update_odometer()
    diff = angle_difference(angle, suzuki.theta)
    if abs(diff) < 1.0:
        return
    direction = 1 if diff > 0 else -1
    turned = 0.0
    last = suzuki.theta
    suzuki.simple(direction * suzuki.SPEED / 2, -direction * suzuki.SPEED / 2)
    while turned < abs(diff):
        suzuki.update_odometer()
        turned += direction * angle_difference(suzuki.theta, last)
        last = suzuki.theta
        sleep(suzuki.LOOP_DOWNTIME)
    suzuki.simple(0, 0)

def distance_to(target_x, target_y):
    a = target_x - suzuki.x_pos
    b = target_y - suzuki.y_pos
    return (a**2 + b**2)**0.5

def face_toward(target_x, target_y):
    a = target_x - suzuki.x_pos
    b = target_y - suzuki.y_pos
    turn_to(degrees(atan2(a, b)) % 360)

def go_toward(target_x, target_y):
    suzuki.go_distance(distance_to(target_x, target_y))

def head():
    pass

def body():
    for waypoint in way_points:
        target_x, target_y = waypoint
        target_x = suzuki.convert_block_to_coordinates(target_x)
        target_y = suzuki.convert_block_to_coordinates(target_y)
        print(target_x, target_y)

        if distance_to(target_x, target_y) > ERROR:
            face_toward(target_x, target_y)
            go_toward(target_x, target_y)

        sleep(0.5)

    raise suzuki.TaskCompleted

suzuki.execute(head, body)
