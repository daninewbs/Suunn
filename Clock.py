import time

from Buttons import Buttons


DIGIT_SPACING = 2

CLOCK_START = (10, 10)

COLON_SIZE = 2
COLON_SPACE = 10

COLON_GAP = 8


class ClockDisplay:
    def __init__(self, screen, time=time.localtime()) -> None:
        self.time = time
        self.screen = screen

    @property
    def hours(self):
        print(self.time)
        return self.time[3] % 24

    @property
    def military_hours(self):
        return self.time[3] % 24

    @property
    def minutes(self):
        return self.time[4]

    @property
    def is_am(self):
        return self.military_hours < 12

    def draw_hours(self, hours):
        if hours < 10:
            self.screen.draw_dig(hours, self._digit_start(1), CLOCK_START[1])
        else:
            for i in range(2):
                self.screen.draw_dig(
                    int(str(hours)[i]), self._digit_start(i), CLOCK_START[1]
                )

    def draw_minutes(self, minutes):
        if minutes < 10:
            self.screen.draw_dig(0, self._digit_start(2) + COLON_GAP, CLOCK_START[1])
            self.screen.draw_dig(
                minutes, self._digit_start(3) + COLON_GAP, CLOCK_START[1]
            )
        else:
            for i in range(2):
                self.screen.draw_dig(
                    int(str(minutes)[i]),
                    self._digit_start(i + 2) + COLON_GAP,
                    CLOCK_START[1],
                )

    def draw_colon(self):
        x = self._digit_start(2) + 3
        y = (
            ((2 * self.screen.V_LENGTH + 3 * self.screen.LINE_SPACE) // 2)
            - COLON_SPACE // 2
            + CLOCK_START[1]
        )
        self.screen.display.fill_rect(x, y, COLON_SIZE, COLON_SIZE, 1)
        self.screen.display.fill_rect(
            x, y + COLON_SPACE // 2, COLON_SIZE, COLON_SIZE, 1
        )

    def __draw_am_pm(self):
        if self.is_am:
            self.screen.print("A M", 100, 10)
        else:
            self.screen.print("P M", 100, 10)

    def draw(self, hours=-1, minutes=-1):
        hours = hours if hours >= 0 else self.hours
        minutes = minutes if minutes >= 0 else self.minutes
        self.draw_hours(hours)
        self.draw_colon()
        self.draw_minutes(minutes)
        self.__draw_am_pm()
        self.screen.display.show()

    def __control_seq(self):
        for i in range(2):
            self.screen.clear()
            time.sleep(0.5)
            self.draw()

    def _digit_start(self, i):
        return CLOCK_START[0] + (i) * (
            (2 * self.screen.LINE_SPACE) + self.screen.H_LENGTH + DIGIT_SPACING
        )

    def __c_min(self, val):
        self.time = time.localtime(time.mktime(self.time) + 60 * val)
        self.draw()

    def __c_hour(self, val):
        self.time = time.localtime(time.mktime(self.time) + pow(60, 2) * val)
        self.draw()


class Alarm(ClockDisplay):
    def __init__(self, screen, time=time.localtime()) -> None:
        super().__init__(screen, time=time)


class LiveClock(ClockDisplay):
    def __init__(self, screen, time=time.localtime()) -> None:
        super().__init__(screen, time=time)


class Watch:
    is_editing_alarm = False

    def __init__(self, screen, live_time=None, alarm_time=None) -> None:
        self.alarm = Alarm(screen=screen, time=alarm_time)
        self.live_clock = LiveClock(screen=screen, time=live_time)
        self.buttons = Buttons()

    @property
    def clock(self):
        return self.alarm if self.is_editing_alarm else self.live_clock

    def toggle_edit(self):
        self.is_editing_alarm = not self.is_editing_alarm

        # set functions for edit mode
        self.buttons.on_a = lambda: self.clock.__c_min(1)
        self.buttons.on_b = lambda: self.clock.__c_min(-1)

        self.__control_seq()
        self.draw()

    def draw(self):
        print(self.clock)
        self.clock.draw()

    def __control_seq(self):
        print(self.clock)
        self.clock.__control_seq()

    def live(self):
        self.draw()

        while True:
            if self.buttons.long_press:

                self.toggle_edit()

                self.buttons.wait_for_input()

