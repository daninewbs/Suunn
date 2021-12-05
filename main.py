# Danielle Newberry &  Ben Allan-Rahill
# code to power sunrise lamp using esp32 feather huzza
from machine import I2C, Pin, PWM
import esp
import neopixel
from Buttons import Buttons
from Clock import Watch
from Screen import Screen
from sh1107 import SH1107_I2C
import time
from pcf8523 import PCF8523
from real_clock import RealClock

# constant colors
BLUE = (100, 149, 237)
PINK = (220, 20, 60)
YELLOW = (255, 215, 0)
GREEN = (0, 255, 0)
PURPLE = (255, 105, 180)
ORANGE = (205, 55, 0)
RED = (205, 0, 0)

LIGHTS = 24
BUZZER_PIN = 25
NEO_PIN = 26
# Set to false to disable testing/tracing code
TESTING = True

# setup for I2C
SDA = Pin(23)
SCL = Pin(22)

pre_set_alarm_hour = 7
pre_set_alarm_min = 30

"""button press causes color to chnage to next one in sequence"""


def change_color(n):
    # set all neopixels to same color
    colors = [BLUE, PINK, YELLOW, GREEN, PURPLE, ORANGE, RED]
    for i in range(LIGHTS):
        np[i] = colors[n]
    np.write()


def light_off():
    for i in range(LIGHTS):
        np[i] = (0, 0, 0)
    np.write()


"""takes as input number of minutes it takes for strip to fade from min to max """


def sunrise(light_minutes):
    np = neopixel.NeoPixel(Pin(NEO_PIN), LIGHTS)  # using 24 pixel ring
    esp.osdebug(None)  # disable debugging

    extra_brightness = 0
    for i in range(light_minutes - 1):
        extra_brightness += 2
        for j in range(LIGHTS):
            np[j] = (i + extra_brightness, i, 0)
            np.write()

        if TESTING:
            time.sleep(0.5)
        else:
            time.sleep(60)  # 60 for once per min


def alarm():
    # buzzer code adapted from: https://micropython-on-wemos-d1-mini.readthedocs.io/en/latest/basics.html#beepers

    beeper = PWM(Pin(BUZZER_PIN), freq=440, duty=512)

    tempo = 5
    tones = {
        "c": 262,
        "d": 294,
        "e": 330,
        "f": 349,
        "g": 392,
        "a": 440,
        "b": 494,
        "C": 523,
        " ": 0,
    }

    melody = "cdefgabC"
    rhythm = [8, 8, 8, 8, 8, 8, 8, 8]

    for tone, length in zip(melody, rhythm):
        beeper.freq(tones[tone])
        time.sleep(tempo / length)

    beeper.deinit()  # TODO: signal this when button pressed


"""uses RTC and checks if it is 30 min before wake up time"""
# adapted from https://github.com/mchobby/esp8266-upy/blob/master/pcf8523/examples/test_alarm.py
def wakeup(h, m):

    # Create an I2C object out of our SDA and SCL pin objects
    i2c = I2C(sda=SDA, scl=SCL)
    rtc = RealClock(i2c)
    rtc = PCF8523(i2c)

    if (
        TESTING
    ):  # sets an alarm that triggers wakeup sequence 20 seconds from current time
        # if you need to set time of rtc
        # rtc.datetime = (2021, 12, 3, 5, 52, 0, 5, 337)

        # Get the current time
        now = rtc.datetime
        print(
            "now   @ Year: %s, month: %s, day: %s, hour: %s, min: %s, sec: %s, weekday: %s, yearday: %s"
            % time.localtime(now)
        )

        # Calculate Alarm 20 sec  in the future
        alarm_time = now + 20
        alarm_tuple = time.localtime(
            alarm_time
        )  # Year, month, day, hour, min, sec, weekday, yearday
        alarm_minutes = alarm_tuple[4]

        # set the alarm for activerate every hour & <alarm_min>
        rtc.alarm_weekday(enable=False)
        rtc.alarm_day(enable=False)
        rtc.alarm_hour(enable=False)
        rtc.alarm_min(alarm_minutes, True)

    else:
        # set the alarm for activate every day at 7:30
        rtc.alarm_weekday(enable=False)
        rtc.alarm_day(enable=False)
        rtc.alarm_hour(h, True)
        rtc.alarm_min(m - 30, True)

    # Activate PCF8523 interrupt pin on alarm. Quite handy to wake-up a microcontroler
    #  Interrupt pin goes to 3.3V on alarm
    # rtc.alarm_interrupt = True
    counter = 0
    while True:
        counter += 1
        print("Testing alarm status, pass %i" % counter)
        if rtc.alarm_status:
            print("Alarm catched!")
            sunrise(10)
            # When lights reach full brightness (at alarm time buzzer goes off)
            alarm()
            print("Reset alarm status ")
            # switch to not wakeup state on button press
            rtc.alarm_status = False
        time.sleep(10)


wakeup(pre_set_alarm_hour, pre_set_alarm_min)


# def wakeup(hour, min):
#     if t.tm_hour == hour and t.tm_min == min - 30 and t.tm_sec == 60:
#         return True


# create FSM
""" modes:
WAKEUP (sunrise sequence)
    trigger 30 min before wakeup time
IDLE (display time light off)
    trigger off button pressed
ON (display time light on -> cycle though colors with each time button pressed changing color)
    trigger color/light button pressed (must be diff than off button)
"""


def display_on():
    print("turn on")
    i2c = I2C(sda=Pin(23), scl=Pin(22), freq=400000)
    screen = Screen(i2c=i2c)


# if TESTING:
#     sunrise(10)  # 30 when not testing
# else:
#     sunrise(30)
# repeat until user presses off button
#  alarm()
# display_on()
i2c = I2C(sda=Pin(23), scl=Pin(22), freq=400000)

screen = Screen(i2c=i2c)
t = time.localtime(time.mktime((2021, 12, 4, 12, 00, 0, 0, 0)))

watch = Watch(screen, live_time=t, alarm_time=t)

watch.live()
