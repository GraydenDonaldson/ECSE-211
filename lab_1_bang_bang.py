from utils.brick import wait_ready_sensors, reset_brick, Motor, EV3UltrasonicSensor
import time

motor_left = Motor(1)    # Set to port id
motor_right = Motor(4)   # Set to port id
sensor = EV3UltrasonicSensor(3)  # Sensor Setup

# ============================================================
# 1) SET THE VARIABLES  (play with these)
# ============================================================
TARGET_DIST = 35      # cm  - distance we want to keep from the wall
TOLERANCE = 3         # cm  - how far off we can be before turning
DANGER_DIST = 25      # cm  20- closer than this -> pivot away RIGHT NOW (no waiting)
SPEED = 30            # power for going straight
TURN_SPEED = 20       # power of the slower wheel when turning
PIVOT_SPEED = 25      # power for pivoting in place
MAX_TURN_TIME = 1     # seconds in turning mode before we pivot
PIVOT_TIME = 0.3      # seconds each pivot lasts
DANGER_PIVOT_TIME = 0.15  # seconds per pivot step when in the danger zone
PIVOT_LIMIT = 3       # this many pivots...
PIVOT_WINDOW = 4      # ...within this many seconds -> long pivot
LONG_PIVOT_MULT = 2   # long pivot = PIVOT_TIME x this
GLITCH_VALUE = 255    # the junk reading to ignore
GLITCH_HOLD_TIME = 1  # seconds it has to stay 255 before we believe it
GAP_JUMP = 20         # cm  - a sudden jump this big = a gap in the wall
GAP_TIME = 0.8        # seconds to drive straight past the gap
LOOP_DELAY = 0.05     # seconds between sensor readings

# ============================================================
# 2) DEFINE SIMPLE, LEFT, RIGHT, STRAIGHT, PIVOT, GAP
# ============================================================
def simple(left_power, right_power):
    motor_left.set_power(left_power)
    motor_right.set_power(right_power)

def straight():
    simple(SPEED, SPEED)

def right():
    simple(SPEED, TURN_SPEED)

def left():
    simple(TURN_SPEED, SPEED)

pivot_times = []      # when recent pivots happened

def pivot(direction):
    global pivot_times
    now = time.time()
    # keep only pivots from the last PIVOT_WINDOW seconds
    pivot_times = [t for t in pivot_times if now - t < PIVOT_WINDOW]
    pivot_times.append(now)
    # too many pivots lately -> pivot longer
    if len(pivot_times) >= PIVOT_LIMIT:
        duration = PIVOT_TIME * LONG_PIVOT_MULT
        pivot_times = []  # start counting again
    else:
        duration = PIVOT_TIME
    if direction == "right":
        simple(PIVOT_SPEED, -PIVOT_SPEED)
    else:
        simple(-PIVOT_SPEED, PIVOT_SPEED)
    time.sleep(duration)

def gap():
    # drive straight past the gap
    # stops early if the wall comes back (= it really was a gap)
    print("GAP -> going straight")
    straight()
    start = time.time()
    while time.time() - start < GAP_TIME:
        d = sensor.get_value()
        if d is not None and d <= TARGET_DIST + TOLERANCE:
            print("wall is back")
            return
        time.sleep(LOOP_DELAY)

# ============================================================
# 3) TURN LOGIC
# ============================================================
wait_ready_sensors()
print("Ready!")

turn_dir = None       # "right", "left", or None (going straight)
turn_start = 0        # when we started the current turn
glitch_start = None   # when the 255 readings started (None = no glitch)
last_dist = None      # previous reading (used to spot gaps)
gap_armed = True      # gap check only works when we're following the wall normally

try:
    while True:
        dist = sensor.get_value()
        print("dist:", dist)

        if dist is None:          # bad reading, skip it
            time.sleep(LOOP_DELAY)
            continue

        # - gap in the wall -> sudden big jump -> go straight past it
        #   (if it's still far after, it was a real corner and we turn normally)
        if (gap_armed and last_dist is not None
                and last_dist <= TARGET_DIST + TOLERANCE
                and dist - last_dist >= GAP_JUMP):
            gap()
            gap_armed = False     # only ONE gap until we're back on the wall
            last_dist = None
            turn_dir = None
            glitch_start = None
            continue
        last_dist = dist

        # back at a normal distance -> gap check can trigger again
        if abs(dist - TARGET_DIST) <= TOLERANCE:
            gap_armed = True

        # - ignore random 255s unless they stay for a while
        if dist >= GLITCH_VALUE:
            if glitch_start is None:
                glitch_start = time.time()
            if time.time() - glitch_start < GLITCH_HOLD_TIME:
                time.sleep(LOOP_DELAY)   # ignore it, keep doing what we were doing
                continue
        else:
            glitch_start = None

        # - WAY too close -> pivot away immediately (strict)
        if dist < DANGER_DIST:
            print("DANGER -> pivot left")
            simple(-PIVOT_SPEED, PIVOT_SPEED)
            time.sleep(DANGER_PIVOT_TIME)
            turn_dir = None
            continue                     # check again right away

        # - if it's too far -> right
        if dist > TARGET_DIST + TOLERANCE:
            if turn_dir != "right":
                turn_dir = "right"
                turn_start = time.time()
            # if in turning mode too long -> pivot
            if time.time() - turn_start > MAX_TURN_TIME:
                pivot("right")
                turn_start = time.time()
            else:
                right()

        # - if it's too close -> left (same as right)
        elif dist < TARGET_DIST - TOLERANCE:
            if turn_dir != "left":
                turn_dir = "left"
                turn_start = time.time()
            if time.time() - turn_start > MAX_TURN_TIME:
                pivot("left")
                turn_start = time.time()
            else:
                left()

        # - else -> straight
        else:
            turn_dir = None
            straight()

        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    pass
finally:
    reset_brick()

