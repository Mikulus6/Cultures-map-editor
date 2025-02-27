import time
from interface.camera import Camera
from interface.const import timeout_duration, frames_per_second


time_fluctuation = 0.01


class TimeoutHandler:
    initialized = False
    def __init__(self, max_duration: int | float = float("inf"), enable_dynamical_max_duration: bool = False):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.max_duration = max_duration
        self.time_start = 0
        self.calls = 0

        self.reference_timer_initialized = False
        self.reference_timer = 0
        self.enable_dynamical_max_duration = enable_dynamical_max_duration

        self.camera_is_moving = False
        self.timeout_suspension = False

    @property
    def time_end(self):
        return self.time_start + self.max_duration

    def check(self):
        if ((time.time() > self.time_end and self.calls > 0) or self.camera_is_moving) and not self.timeout_suspension:
            raise TimeoutError
        self.calls += 1

    def start(self):
        self.time_start = time.time()
        self.calls = 0

        self.reference_timer_split(time_now = time.time())

    def reference_timer_split(self, *, time_now = None):

        current_time = time.time() if time_now is None else time_now

        if not self.reference_timer_initialized:
            self.reference_timer_initialized = True
            self.reference_timer = current_time
            return

        current_delta_time = current_time - self.reference_timer
        expected_delta_time = 1/frames_per_second

        if abs(expected_delta_time - current_delta_time) < time_fluctuation or\
           not self.enable_dynamical_max_duration :
            pass
        elif expected_delta_time < current_delta_time:
            self.max_duration -= 0.01
        else:
            self.max_duration += 0.01

        self.reference_timer = current_time

    def get_camera_move_status(self, camera: Camera):
        # Necessary to make immediate timeout when camera is moving for smoothness
        self.camera_is_moving = camera.is_moving


timeout_handler = TimeoutHandler(max_duration=timeout_duration, enable_dynamical_max_duration=False)
