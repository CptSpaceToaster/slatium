import threading
from slatium.sides import SlackSide
from .thread_watcher import ThreadWatcher


def main():
    watcher = ThreadWatcher()
    threads = {}
    needs_exit = threading.Event()

    def callback(name):
        print('{0} issued a callback'.format(name))
        if needs_exit.is_set():
            return
        threads[name].reinit()
        threads[name].start()

    class SideHolder():
        def __init__(self, name, side_type, *args, **kwargs):
            self.side_type = side_type
            self.args = args + (name, watcher, callback, needs_exit)
            self.kwargs = kwargs
            self.thread = self.side_type(*self.args, **self.kwargs)

        def reinit(self):
            self.thread = self.side_type(*self.args, **self.kwargs)

        def start(self, *args, **kwargs):
            return self.thread.start(*args, **kwargs)

        def close(self, *args, **kwargs):
            return self.thread.close(*args, **kwargs)

        def is_alive(self, *args, **kwargs):
            return self.thread.is_alive(*args, **kwargs)

    print('Main: {0}'.format(threading.current_thread()))
    threads['slack'] = SideHolder('slack', SlackSide, 'xoxb-14766807600-AgenL9nrFmnTtGgJ8W81HuUX', kwargs={'ping_interval': 30})
    for name, thread in threads.items():
        thread.start()

    # idle until needs_exit
    needs_exit.wait()

    # cleanup
    for name, thread in threads.items():
        if thread.is_alive:
            print('Closing: {0}'.format(thread))
            thread.close()
