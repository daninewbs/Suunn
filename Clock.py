import time


DIGIT_SPACING = 2

CLOCK_START = (10, 10)

COLON_SIZE = 2
COLON_SPACE = 10

COLON_GAP = 8


class Alarm:
    def __init__(self, time=time.localtime()) -> None:
        self.time = time

    @property
    def hours(self):
        return self.time[3] % 12

    @property
    def military_hours(self):
        return self.time[3]

    @property
    def minutes(self):
        return self.time[4]

    @property
    def is_am(self):
        return self.military_hours < 12

    def c_min(self, val):
        print(self.time)
        self.time = time.localtime(time.mktime(self.time) + 60 * val)

    def c_hour(self, val):
        self.time = time.localtime(time.mktime(self.time) + pow(60, 2) * val)


class Clock:
    alarm: Alarm
    is_editing_alarm = False

    def __init__(self, screen, time=time.localtime()) -> None:
        self.time = time
        self.screen = screen
        self.alarm = Alarm()

    @property
    def hours(self):
        return self.time[3] % 12

    @property
    def military_hours(self):
        return self.time[3]

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

    def draw_clock(self, hours=-1, minutes=-1):
        hours = hours if hours >= 0 else self.hours
        minutes = minutes if minutes >= 0 else self.minutes
        self.draw_hours(hours)
        self.draw_colon()
        self.draw_minutes(minutes)
        self.__draw_am_pm()
        self.screen.display.show()

    def __draw_alarm(self):
        h = self.alarm.hours
        m = self.alarm.minutes
        print(m)
        self.draw_clock(h, m)

    def __control_seq(self):
        for i in range(2):
            self.screen.clear()
            time.sleep(0.5)
            self.draw_clock()

    def _digit_start(self, i):
        return CLOCK_START[0] + (i) * (
            (2 * self.screen.LINE_SPACE) + self.screen.H_LENGTH + DIGIT_SPACING
        )

    def change_a_min(self, diff):
        self.alarm.c_min(diff)
        self.__draw_alarm()

    def change_a_hour(self, diff):
        self.alarm.c_hour(diff)
        self.__draw_alarm()

    def toggle_edit(self):
        self.is_editing_alarm = not self.is_editing_alarm
        self.__control_seq()
        if self.is_editing_alarm:
            # draw alarm
            self.__draw_alarm()
        else:
            self.draw_clock()
