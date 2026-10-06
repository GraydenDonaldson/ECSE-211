from utils.brick import wait_ready_sensors, reset_brick, Motor, EV3UltrasonicSensor
import time
from enum import Enum

motor_left = Motor(1)    # Set to port id
motor_right = Motor(4)   # Set to port id
sensor = EV3UltrasonicSensor(3)  # Sensor Setup

# ============================================================
# 1) SET THE VARIABLES  (play with these)
# ============================================================

TARGET_DISTANCE = 35  # cm  - distance we want to keep from the wall

HARD_TURN = 7         # cm - the distance range from band center to trigger a harder turn

MAX_DISTANCE = 20     # cm - the distance from band center to trigger a hard pivot

SPEED = 30            # power for going straight

HARD_TURN_SPEED = 15  # power of the slower wheel when turning hard

LIGHT_TURN_SPEED = 25 # power of the slower wheel when turning lightly

PIVOT_SPEED = 25      # power for pivoting in place

PIVOT_TIME = 0.2      # the length of time to pivot for

LOOP_DELAY = 0.05     # seconds between sensor readings

GAP_TIME = 0.9        # seconds to drive straight past the gap

GAP_IGNORE = 0.5      # seconds to ignore 255 without making changes

GAP_DISTANCE = 255    # distance that indicates a gap

TURN_DOWNTIME = 0.2   # time to let a turn execute

STRAIGHT_DOWNTIME = 0.2

# ============================================================
# 2) DEFINE SIMPLE, LEFT, RIGHT, STRAIGHT, PIVOT, GAP
# ============================================================
class direction(Enum):
    Left = 0
    Right = 1
    
class strength(Enum):
    Hard = 0
    Light = 1
    
def simple(left_power, right_power):
    motor_left.set_power(left_power)
    motor_right.set_power(right_power)

def straight():
    simple(SPEED, SPEED)
    time.sleep(STRAIGHT_DOWNTIME)

def turn(d: direction, s: strength):
    turn_strength = LIGHT_TURN_SPEED if s == strength.Light else HARD_TURN_SPEED
    if d == direction.Left:
        simple(turn_strength, SPEED)
    else:
        simple(SPEED, turn_strength)
        
    time.sleep(TURN_DOWNTIME)
        
def pivot(d: direction):
    if d == direction.Left:
       simple(-PIVOT_SPEED, PIVOT_SPEED)
    else:
        simple(PIVOT_SPEED, -PIVOT_SPEED)
    time.sleep(PIVOT_TIME)
        
def eval_and_set_turn(dist, d : direction):
    difference = abs(dist - TARGET_DISTANCE)
    if difference > MAX_DISTANCE:
        print("Pivot", d)
        pivot(d)
        straight()
    elif difference > HARD_TURN:
        print("Hard Turn", d)
        turn(d, strength.Hard)
    else:
        print("Light Turn", d)
        turn(d, strength.Light)
        
    
    
# ============================================================
# 3) MAIN BODY
# ============================================================
wait_ready_sensors()
print("Ready!")





try:
    
    since_gap_start = time.time()
    while True:
        dist = sensor.get_value()
        #print("dist:", dist)

        if dist is None:          # bad reading, skip it
            time.sleep(LOOP_DELAY)
            continue
        
        # Gap Logic
        if dist >= GAP_DISTANCE:
            # Currently at a gap with but not long enough to turn
            time_dif = abs(time.time() - since_gap_start)
            
            if time_dif < GAP_IGNORE:
                turn(direction.Left, strength.Light)
                continue
            
            elif time_dif < GAP_TIME:
                turn(direction.Right, strength.Light)
                continue
            else:
                print("END GAP")
                pivot(direction.Right)
                straight()

    
        else:
            # Not at a gap, reset gap time
            since_gap_start = time.time()
        
        
        # Turn Logic
        if dist > TARGET_DISTANCE:
            eval_and_set_turn(dist, direction.Right)
        elif dist < TARGET_DISTANCE:
            eval_and_set_turn(dist, direction.Left)
        else:
            straight()

        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    pass
finally:
    reset_brick()
    
    


