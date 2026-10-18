from robot import Robot

robot = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)


def lab_setup():
    pass
def lab():
    for i in range(4):
        robot.go_distance(90)
        robot.turn_right_angle(90)
    raise robot.TaskCompleted

robot.execute(lab_setup, lab)