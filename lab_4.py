#Lab 4
from robot import Robot
from time import sleep

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", arm_motor_id = "C", left_light_sensor_id=1, right_light_sensor_id=3)

drop_turn = 15
sleep_time = 1
angle = 40
x_correction = 3
y_correction = 14

ERROR = 5 # cm
DISTANCE_TO_BACK = 15 # Cm

# We always start at 0,0 so update position
suzuki.x_pos = 0
suzuki.y_pos = 0

#slow down the arm

suzuki.arm_motor.set_limits(dps=200)

# Take waypoints from terminal
way_points = []
dropped = [False, False, False, False]

def drop_block():
    suzuki.arm_motor.set_position_relative(angle)
    sleep(1)
    suzuki.arm_motor.set_position_relative(-angle)
    sleep(1)
    suzuki.arm_motor.float_motor()

def go_toward_waypoint(direction, distance, point_num):
    suzuki.face_angle(direction)
    suzuki.go_distance(DISTANCE_TO_BACK)
    if point_num > 0 and not dropped[point_num-1]:
        drop_block()
        dropped[point_num-1] = True
    suzuki.go_distance(distance - DISTANCE_TO_BACK)

for i in range (4):
    x = int(input(f"X coordinate {i+1}: "))
    y = int(input(f"Y coordinate {i+1}: "))
    way_points.append((x, y))

def head():
    pass

def body():
    block_num = 0
    for waypoint in way_points:
        target_x, target_y = waypoint
        target_x = suzuki.convert_block_to_coordinates(target_x)
        target_y = suzuki.convert_block_to_coordinates(target_y)
        print(target_x, target_y)
        print(suzuki.x_pos, suzuki.y_pos)
        if abs(target_x - suzuki.x_pos) > ERROR:
            if target_x > suzuki.x_pos:
                print("increase x")
                go_toward_waypoint(90, target_x-suzuki.x_pos, block_num)
            elif target_x < suzuki.x_pos:
                print("decrease x")
                go_toward_waypoint(270, suzuki.x_pos-target_x, block_num)
        if abs(target_y - suzuki.y_pos) > ERROR:
            if target_y > suzuki.y_pos:
                print("increase y")
                go_toward_waypoint(0, target_y-suzuki.y_pos, block_num)
            elif target_y < suzuki.y_pos:
                print("decrease y")
                go_toward_waypoint(180, suzuki.y_pos-target_y, block_num)
        block_num += 1
    go_toward_waypoint(suzuki.theta, 15, 4)

    print("all blocks dropped")
    raise suzuki.TaskCompleted

suzuki.execute(head, body)


#dropping logic for first drop (motor is outside of pipe)
    #turn motor 3 TURN

#dropping logic for other drops (motor is still under pipe)
    #turn motor 3 -TURN
    #wait 0.5
    #turn motor 3 TURN

#go to next drop
    
