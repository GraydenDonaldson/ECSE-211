from robot import Robot

r = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)
def body():
    print(r.x_pos, r.y_pos, r.theta)
r.execute(body)