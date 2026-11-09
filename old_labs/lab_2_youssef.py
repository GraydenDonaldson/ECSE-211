from utils.brick import wait_ready_sensors, reset_brick, Motor, NXTColorSensor, EV3ColorSensor
import math, time, threading

MODE = "square"    # "test" -> print raw sensor/encoder values, "float" -> TA wheel test, "square" -> demo

left_motor = Motor("A")
right_motor = Motor("B")
ls = EV3ColorSensor(4)    # left light sensor og 3 works
rs = NXTColorSensor(3)    # right light sensor

# ============================================================
# VARIABLES  (calibrate these)
# ============================================================
WHEEL_RADIUS = 3.0        # cm   -> adjust if distance is off
TRACK_WIDTH = 10.0        # cm   -> adjust if angle is off
TILE = 30.48              # cm   (Figure 2)
LIGHT_OFFSET = 4.0        # cm, wheel center -> light sensor (along heading)

ENC_SIGN_L = 1            # flip to -1 if a motor's encoder counts backward when driving forward
ENC_SIGN_R = 1

SPEED = 12                # forward power
TURN_POWER = 20           # power while turning in place
CREEP_POWER = 15          # power of the wheel that's still moving while aligning
TURN_TOLERANCE = 2.0      # deg, stop turning this close to target
LINE_RATIO = 0.6          # reading < baseline * ratio  -> "black line"
MIN_LINE_GAP = 10         # cm, ignore new lines until we've moved this far past the last one
ALIGN_TIMEOUT = 1.5       # s, give up waiting for the 2nd sensor
SIDES = 4
TILES_PER_SIDE = 3

# ============================================================
# ODOMETER  (x, y in cm; theta stored in radians, 0 = +y, clockwise positive)
# ============================================================
x, y, theta = 0.0, 0.0, 0.0
prev_L, prev_R = 0, 0
lock = threading.Lock()
running = True

def update_odometer():
    global x, y, theta, prev_L, prev_R
    with lock:
        L = ENC_SIGN_L * left_motor.get_encoder()
        R = ENC_SIGN_R * right_motor.get_encoder()
        dL = math.radians(L - prev_L) * WHEEL_RADIUS
        dR = math.radians(R - prev_R) * WHEEL_RADIUS
        prev_L, prev_R = L, R
        d = (dL + dR) / 2
        dtheta = (dL - dR) / TRACK_WIDTH      # left fwd + right back -> theta increases
        x += d * math.sin(theta + dtheta / 2)
        y += d * math.cos(theta + dtheta / 2)
        theta = (theta + dtheta) % (2 * math.pi)

def odometer_loop():
    while running:
        update_odometer()
        time.sleep(0.01)

def get_theta_deg():
    return math.degrees(theta) % 360

def display():
    while running:
        t = round(get_theta_deg(), 1)
        if t >= 360.0:                         # keep range [0, 359.9]
            t = 0.0
        print(f"x={x:.1f} cm  y={y:.1f} cm  theta={t:.1f} deg")
        time.sleep(0.5)

# ============================================================
# MOTOR HELPERS
# ============================================================
def simple(left_power, right_power):
    left_motor.set_power(left_power)
    right_motor.set_power(right_power)

def stop():
    simple(0, 0)

def float_motors():
    left_motor.float_motor()
    right_motor.float_motor()

    while(True):
        update_odometer()
        time.sleep(0.01)

# ============================================================
# LIGHT SENSORS
# ============================================================
def read_light(sensor):
    # Average of the RGB channels. Black line -> low, orange tile -> high.
    # (If your sensor class exposes something else, change it here only.)
    rgb = sensor.get_rgb()
    if rgb is None:
        return None
    return sum(rgb[:3]) / 3

def calibrate_baseline(sensor, n=15):
    vals = []
    while len(vals) < n:
        v = read_light(sensor)
        if v is not None:
            vals.append(v)
        time.sleep(0.05)
    return sum(vals) / len(vals)

base_l, base_r = 1.0, 1.0

def on_line(sensor, base):
    v = read_light(sensor)
    return v is not None and v < base * LINE_RATIO

# ============================================================
# LIGHT CORRECTION
# ============================================================
def snap_to_line():
    """Both sensors are on a line -> robot is perpendicular to it.
    Snap theta to the nearest multiple of 90 and the travel-axis
    coordinate to the nearest grid line (minus the sensor offset)."""
    global x, y, theta
    with lock:
        h = (round(math.degrees(theta) / 90) * 90) % 360
        theta = math.radians(h)
        if h in (0, 180):                      # moving along y
            sensor_pos = y + LIGHT_OFFSET * math.cos(theta)
            k = round(sensor_pos / TILE)
            y = k * TILE - LIGHT_OFFSET * math.cos(theta)
        else:                                  # moving along x
            sensor_pos = x + LIGHT_OFFSET * math.sin(theta)
            k = round(sensor_pos / TILE)
            x = k * TILE - LIGHT_OFFSET * math.sin(theta)
    print(f"CORRECTED -> x={x:.1f} y={y:.1f} theta={get_theta_deg():.1f}")

def drive_to_line():
    """Drive forward until a line is hit, align both sensors on it, then correct odometer."""
    simple(SPEED, SPEED)
    while True:
        l = on_line(ls, base_l)
        r = on_line(rs, base_r)
        if l or r:
            break
        time.sleep(0.01)

    # one side hit first -> stop that wheel, creep the other until its sensor hits too
    start = time.time()
    if l and not r:
        simple(0, CREEP_POWER)
        while not on_line(rs, base_r) and time.time() - start < ALIGN_TIMEOUT:
            time.sleep(0.01)
    elif r and not l:
        simple(CREEP_POWER, 0)
        while not on_line(ls, base_l) and time.time() - start < ALIGN_TIMEOUT:
            time.sleep(0.01)
    stop()

    if on_line(ls, base_l) and on_line(rs, base_r):
        snap_to_line()
    else:
        print("align timeout -> no correction")

def drive_distance(cm):
    """Drive straight forward by cm (measured by the odometer)."""
    x0, y0 = x, y
    simple(SPEED, SPEED)
    while math.hypot(x - x0, y - y0) < cm:
        time.sleep(0.01)

# ============================================================
# TURNING (in place, to the right)
# ============================================================
def turn_right_to(target_deg):
    while True:
        err = (target_deg - get_theta_deg() + 540) % 360 - 180   # signed, + means still need to turn right
        if err <= TURN_TOLERANCE:
            break
        simple(TURN_POWER, -TURN_POWER)       # left fwd, right back -> theta increases
        time.sleep(0.005)
    stop()
    time.sleep(0.2)

# ============================================================
# SQUARE DRIVER
# ============================================================
def square_driver():
    for side in range(SIDES):
        for line in range(TILES_PER_SIDE):
            drive_to_line()
            if line < TILES_PER_SIDE - 1:
                drive_distance(MIN_LINE_GAP)  # move off the line before looking for the next
        # sensors are on the corner line; wheel center is LIGHT_OFFSET short of it
        drive_distance(LIGHT_OFFSET)
        stop()
        time.sleep(0.2)
        turn_right_to(((side + 1) * 90) % 360)
        drive_distance(MIN_LINE_GAP) if side < SIDES - 1 else None
    stop()
    print("Done.")

# ============================================================
# MAIN
# ============================================================
try:
    wait_ready_sensors()
    prev_L = ENC_SIGN_L * left_motor.get_encoder()
    prev_R = ENC_SIGN_R * right_motor.get_encoder()

    threading.Thread(target=display, daemon=True).start()

    if MODE == "float":
        float_motors()                         # blocks; updates odometer itself

    elif MODE == "test":
        while True:
            print("L enc:", left_motor.get_encoder(), "R enc:", right_motor.get_encoder(),
                  "| ls:", read_light(ls), "rs:", read_light(rs))
            time.sleep(0.5)

    elif MODE == "square":
        base_l = calibrate_baseline(ls)        # robot must start on a tile (not on a line)
        base_r = calibrate_baseline(rs)
        print("baselines:", base_l, base_r)
        threading.Thread(target=odometer_loop, daemon=True).start()
        square_driver()
        while True:
            time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    running = False
    stop()
    reset_brick()
