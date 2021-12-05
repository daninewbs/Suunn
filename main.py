# Danielle Newberry &  Ben Allan-Rahill
# code to power sunrise lamp using esp32 feather huzza
from machine import I2C, Pin, PWM
import esp
import neopixel
from suunn.Buttons import Buttons
from suunn.Clock import Watch
from suunn.Screen import Screen
from suunn.sh1107 import SH1107_I2C
import time
from suunn.pcf8523 import PCF8523
from suunn.real_clock import RealClock
import random
import network
import time
from suunn.subpub import MQTT

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
TESTING = False

# setup for I2C
SDA = Pin(23)
SCL = Pin(22)

pre_set_alarm_hour = 7
pre_set_alarm_min = 30

"""button press causes color to chnage to next one in sequence"""


"""takes as input number of minutes it takes for strip to fade from min to max """


"""uses RTC and checks if it is 30 min before wake up time"""
# adapted from https://github.com/mchobby/esp8266-upy/blob/master/pcf8523/examples/test_alarm.py


# wakeup(pre_set_alarm_hour, pre_set_alarm_min)


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


class Suunn:
    # STATES
    states = {"IDLE": 0, "SUNRISE": 1, "EDIT_ALARM": 2}

    current_state = 0
    next_state = 0

    def __init__(self) -> None:
        self.i2c = I2C(sda=Pin(23), scl=Pin(22), freq=400000)
        self.np = neopixel.NeoPixel(Pin(NEO_PIN), LIGHTS)  # using 24 pixel ring

        self.color_index = 0

        screen = Screen(i2c=self.i2c)
        self.rtc = PCF8523(self.i2c)
        print(time.localtime(self.rtc.datetime))

        self.watch = Watch(
            screen,
            live_time=time.localtime(self.rtc.datetime),
            alarm_time=time.localtime(self.rtc.datetime),
            rtc=self.rtc,
        )

        # Create an I2C object out of our SDA and SCL pin objects

        # MQTT
        self.mqtt_client = MQTT()

    def idle__(self):
        light_on = False

        def toggle_light():
            nonlocal light_on
            light_on = not light_on
            if not light_on:
                self.light_off()
            else:
                self.change_color(random.randint(0, 6))

        def cycle_color():
            global color_index
            self.color_index += 1
            self.color_index %= 6
            self.change_color(self.color_index)

        self.watch.buttons.on_a = toggle_light
        self.watch.buttons.on_b = cycle_color

        while True:
            self.watch.live()
            # check for edit button press
            if self.watch.check_for_edit():
                print("IN EDIT!!")
                # GO TO ALARM EDIT STATE
                self.next_state = self.states["EDIT_ALARM"]
                break

            # check for button input
            self.watch.buttons.check_for_input()

            # check for MQTT msg

            self.mqtt_client.client.check_msg()

            # check if alarm is triggered
            if self.rtc.alarm_status:
                print("ALARM!!")
                # GO TO SUNRISE STATE
                self.next_state = self.states["SUNRISE"]
                break

    """EDIT ALARM STATE """

    def edit_alarm__(self):
        # wait for the user to keep editing the alarm
        new_alarm_time = self.watch.turn_on_edit()

        self.save_alarm(new_alarm_time[3], new_alarm_time[4])

        # set the next state
        self.next_state = self.states["IDLE"]

    def sunrise__(self):
        self.watch.live()
        self.sunrise(10)  # ten minutes
        self.alarm()

        # GO BACK TO IDLE STATE
        self.next_state = self.states["IDLE"]

    def save_alarm(self, h, m):

        if (
            TESTING
        ):  # sets an alarm that triggers wakeup sequence 20 seconds from current time
            # if you need to set time of rtc
            # rtc.datetime = (2021, 12, 3, 5, 52, 0, 5, 337)

            # Get the current time
            now = self.rtc.datetime
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
            self.rtc.alarm_weekday(enable=False)
            self.rtc.alarm_day(enable=False)
            self.rtc.alarm_hour(enable=False)
            self.rtc.alarm_min(alarm_minutes, True)

        else:
            # set the alarm for activate every day at 7:30
            self.rtc.alarm_weekday(enable=False)
            self.rtc.alarm_day(enable=False)
            self.rtc.alarm_hour(h, True)
            self.rtc.alarm_min(m, True)

    def alarm(self):
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
        alarm_on = True

        def alarm_off():
            nonlocal alarm_on
            print("alarm off!!")
            alarm_on = False
            self.rtc.alarm_status = False

        self.watch.buttons.on_b = lambda: alarm_off()
        while alarm_on:
            for tone, length in zip(melody, rhythm):
                self.watch.buttons.check_for_input()
                if not alarm_on:
                    break
                beeper.freq(tones[tone])
                time.sleep(tempo / length)

        beeper.deinit()  # TODO: signal this when button pressed

    def sunrise(self, light_minutes):
        esp.osdebug(None)  # disable debugging

        extra_brightness = 0
        for i in range(light_minutes - 1):
            extra_brightness += 2
            for j in range(LIGHTS):
                self.np[j] = (i + extra_brightness, i, 0)
                self.np.write()

            time.sleep(0.5)  # 60 for once per min

    def change_color(self, n):
        # set all neopixels to same color
        colors = [BLUE, PINK, YELLOW, GREEN, PURPLE, ORANGE, RED]
        for i in range(LIGHTS):
            self.np[i] = colors[n]
        self.np.write()

    def light_off(self,):
        for i in range(LIGHTS):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def start(self):
        # START THE FSM
        while True:
            print(self.current_state)
            if self.current_state == self.states["IDLE"]:
                self.idle__()
            elif self.current_state == self.states["SUNRISE"]:
                self.sunrise__()
            elif self.current_state == self.states["EDIT_ALARM"]:
                self.edit_alarm__()

            # end loop
            self.current_state = self.next_state


sun = Suunn()

sun.start()
