import threading
import weakref
import functools


class ThreadWatcher(object):
    """
    Stolen from this wonderful blog post:
    https://emptysqua.re/blog/knowing-when-a-python-thread-has-died/

    Basically, we perform a callback when the locals are cleaned up for each
    thread, by cramming an empty Vigil object in each thread, and running
    _on_death when Python makes it go away.

    This was written at a time when Python2.7 was a cool thing... I'm not sure
    if there's a better way to do this in 3.4, or if anything should change
    a significant amount.
    """
    class Vigil(object):
        pass

    def __init__(self):
        self._refs = {}
        self._local = threading.local()

    def _on_death(self, vigil_id, callback, name, ref):
        self._refs.pop(vigil_id)
        callback(name)

    def watch(self, callback, name):
        if not self.is_watching():
            self._local.vigil = v = ThreadWatcher.Vigil()
            on_death = functools.partial(self._on_death, id(v), callback, name)

            ref = weakref.ref(v, on_death)
            self._refs[id(v)] = ref

    def is_watching(self):
        "Is the current thread being watched?"
        return hasattr(self._local, 'vigil')

    def unwatch(self):
        try:
            v = self._local.vigil
            del self._local.vigil
            self._refs.pop(id(v))
        except AttributeError:
            pass
