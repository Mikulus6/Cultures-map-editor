import time

class Report:
    def __init__(self, *, muted: bool = False):
        self.time_init = time.time()
        self.output_counter = 0
        self.muted = muted

    @property
    def duration_str(self):
        duration = round(time.time() - self.time_init)

        hours = duration // 3600
        minutes = (duration - hours * 3600) // 60
        seconds = (duration - hours * 3600 - minutes * 60)
        return f"{'%02d' % hours}:{'%02d' % minutes}:{'%02d' % seconds}"

    def report(self, text: str):
        print_text = f"[{self.duration_str}] {text}"
        if not self.muted: print(print_text)
        return print_text
