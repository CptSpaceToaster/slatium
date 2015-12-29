import threading


class Side(threading.Thread):
    def __init__(self, name, watcher, callback, needs_exit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.watcher = watcher
        self.callback = callback
        self.needs_exit = needs_exit

    def send_message(self, message, channel, name):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def run(self):
        self.watcher.watch(self.callback, self.name)
        super().run()
