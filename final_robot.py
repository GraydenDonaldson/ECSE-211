from utils.brick import Motor, EV3ColorSensor, NXTColorSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick

class FinalRobot:

    def __init__(self, left_motor_id, right_motor_id, conveyer_motor_id, storage_motor_id left_light_sensor_id, right_light_sensor_id, ultrasonic_sensor_id, left_sensor_of_type_EV3):
        """
        Instantiates the robot, taking the port ids to connect to the sensors and motors, waits until sensors are ready to exit

        Args:
            left_motor_id (str): the port ID of the left motor
            right_motor_id (str): the port ID of the right motor
            conveyer_motor_id (str): the port ID of the conveyer belt motor
            storage_motor_id (str): the port ID of the storage emptying motor
            left_light_sensor_id (int: the port ID of the left light sensor
            right_light_sensor_id (int): the port ID of the right light sensor
            ultrasonic_sensor_id (int): the port ID of the ultrasonic sensor
        """

        # Motors
        self.left_motor = Motor(left_motor_id)
        self.right_motor = Motor(right_motor_id)
        self.conveyer_motor = Motor(conveyer_motor_id)
        self.storage_motor = Motor(storage_motor_id)

        # Sensors
        
