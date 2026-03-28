
from machine import Pin, ADC
from time import ticks_ms, ticks_diff, sleep
import motors
import btconnection

# motor PINs
PIN_MOTOR_LEFT = 14
PIN_MOTOR_RIGHT = 27

# start PIN
PIN_START_BTN = Pin(17, Pin.IN)

# sensors
left_transistor = ADC(Pin(35))
right_transistor = ADC(Pin(34))
left_transistor.atten(ADC.ATTN_11DB)
right_transistor.atten(ADC.ATTN_11DB)

start_button = Pin(PIN_START_BTN, Pin.IN)

motors_obj = motors.Motors(PIN_MOTOR_LEFT, PIN_MOTOR_RIGHT)

# base speed
PWM_SPEED = 55

# Bluetooth function and object
def receive(data):
    print(data)
uart = btconnection.BLEUART(receive)

# line threshold
THRESHOLD = 1

# variables
gap_start_time = 0
in_gap = False
gap_counter = 0                  # large gaps
gap_counted_already = False      # count gaps only once

bias_start_time = 0
bias_completed = False
global_bias = "unknown"          # "left" or "right"
corrections_l_counter = 0
corrections_r_counter = 0

last_white_detected = 0

# constants
MIN_GAP_DURATION_TO_COUNT = 1300
BIAS_FINDING_TIME = 3500         # 3.5 sec to determine global bias

while True:
    if start_button.value():     # start
        sleep(0.1)

        print("Rover initializes")
        uart.send("Rover initializes\n")

        # reset all variables at the beginning
        bias_start_time = ticks_ms()
        bias_completed = False
        global_bias = "unknown"
        corrections_l_counter = 0
        corrections_r_counter = 0

        gap_counter = 0
        gap_counted_already = False

        sleep(1.5)
        motors_obj.drive_straight(100, 0.001) # starting boost 1 msec

        while True:
            left_value = left_transistor.read_uv() / 1e6   # measurement left
            right_value = right_transistor.read_uv() / 1e6 # measurement right

            if not bias_completed:
                if ticks_diff(ticks_ms(), bias_start_time) > BIAS_FINDING_TIME:
                    bias_completed = True

                    if corrections_l_counter > corrections_r_counter:
                        global_bias = "left"
                        print("Bias determined: left turn")
                        uart.send("Bias determined: left turn\n")
                    else:
                        global_bias = "right"
                        print("Bias determined: right turn")
                        uart.send("Bias determined: right turn\n")

            # drive
            if left_value >= THRESHOLD and right_value >= THRESHOLD:
                motors_obj.drive_straight(PWM_SPEED, 0.01)

            elif left_value < THRESHOLD and right_value >= THRESHOLD:
                motors_obj.turn_right(PWM_SPEED, 0.01)
                if not bias_completed:
                    corrections_r_counter += 1                            

            elif left_value >= THRESHOLD and right_value < THRESHOLD:
                motors_obj.turn_left(PWM_SPEED, 0.01)
                if not bias_completed:
                    corrections_l_counter += 1            

            elif left_value < THRESHOLD and right_value < THRESHOLD:
                if last_white_detected == 0:
                    last_white_detected = ticks_ms()
                if not in_gap and ticks_diff(ticks_ms(), last_white_detected) > 50:
                    gap_start_time = ticks_ms()                                # measures gap time
                    in_gap = True
                    gap_counted_already = False
                    uart.send("Gap found\n") 
                if in_gap:        
                    gap_duration = ticks_diff(ticks_ms(), gap_start_time)      # time needed to cross gap

                    # recognize exit gap
                    if not gap_counted_already:
                        if gap_duration > MIN_GAP_DURATION_TO_COUNT:               
                            gap_counter += 1                                       
                            gap_counted_already = True                             # gap recognized
                            print("That's the exit gap. Encounter number:", gap_counter)
                            uart.send("That's the exit gap. Encounter number: " + str(gap_counter)  + "\n")

                            # rover leaves through exit gap during second crossing
                            if gap_counter >= 2:
                                print("EXIT SEQUENCE")
                                uart.send("EXIT SEQUENCE\n")
                                
                                if global_bias == "left":
                                    motors_obj.turn_right(85, 0.01) # strong right 
                                else:
                                    motors_obj.turn_left(85, 0.01)  # Strong left
                                sleep(1.0)                                  
                                motors_obj.drive_straight(0, 0)     # motors off
                                print("Finished")
                                uart.send("Finished\n")
                                while True:                         # rover sleep until reset
                                    sleep(0.1)

                    motors_obj.drive_straight(PWM_SPEED, 0.01)
            
            if left_value >= THRESHOLD or right_value >= THRESHOLD: # reset in_gap when line found again
                in_gap = False
                last_white_detected = 0                             # reset timer

            
