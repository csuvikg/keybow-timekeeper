import time
import keybow
from transitions import Machine
from enum import Enum, auto


keybow.setup(keybow.MINI)


class State(Enum):
    OFF = auto()
    DECIDE_ON_TASK = auto()
    WORKING = auto()
    WORKING_PAUSED = auto()
    BREAK = auto()
    BREAK_PAUSED = auto()


# { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid', 'prepare': ['heat_up', 'count_attempts'], 'conditions': 'is_really_hot', 'after': 'stats'},
transitions = [
    {'trigger': 'start', 'source': State.OFF, 'dest': State.DECIDE_ON_TASK, 'prepare': ['change_color']},
    {'trigger': 'decide', 'source': State.DECIDE_ON_TASK, 'dest': State.WORKING, 'prepare': ['change_color']},
    {'trigger': 'pause', 'source': State.WORKING, 'dest': State.WORKING_PAUSED, 'prepare': ['change_color']},
    {'trigger': 'resume', 'source': State.WORKING_PAUSED, 'dest': State.WORKING, 'prepare': ['change_color']},
    {'trigger': 'finish', 'source': State.WORKING, 'dest': State.BREAK, 'prepare': ['change_color']},
    {'trigger': 'pause', 'source': State.BREAK, 'dest': State.BREAK_PAUSED, 'prepare': ['change_color']},
    {'trigger': 'resume', 'source': State.BREAK_PAUSED, 'dest': State.BREAK, 'prepare': ['change_color']},
    {'trigger': 'start_next', 'source': State.BREAK, 'dest': State.DECIDE_ON_TASK, 'prepare': ['change_color']},
]


led_color = {
    State.OFF: (0, 0, 0),
    State.DECIDE_ON_TASK: (50, 0, 50),
    State.WORKING: (0, 50, 0),
    State.WORKING_PAUSED: (50, 50, 0),
    State.BREAK: (50, 0, 0),
    State.BREAK_PAUSED: (50, 50, 0),
}


class Timekeeper(Machine):
    timer_start = 0
    turns = 0
    def increment_turns(self): self.turns += 1

    def change_color(self):
        r, g, b = led_color[self.state]
        keybow.set_led(1, r, g, b)

    def __init__(self):
        Machine.__init__(self, states=State, initial=State.OFF, transitions=transitions)


timekeeper = Timekeeper()

on_press = {
    State.OFF: timekeeper.start,
    State.DECIDE_ON_TASK: timekeeper.decide,
    State.WORKING: timekeeper.pause,
    State.WORKING_PAUSED: timekeeper.resume,
    State.BREAK: timekeeper.pause,
    State.BREAK_PAUSED: timekeeper.resume,
}

pressed = dict()


@keybow.on()
def handle_key(index, state):
    pressed[index] = state
    if not state:
        on_press[timekeeper.state]()


while True:
    keybow.show()
    time.sleep(1.0 / 60.0)

