import multiprocessing
import os
import signal
from .dicts import Dualdict


def handleSIGCHLD(signum, frame):
    # obtain the pid of the child that died
    pid, status = os.waitpid(-1, 0)

    # Restart the process
    if pid in procs:
        procs[pid].renew_process()
        procs[pid].start()


# Bind handler to SIGCHLD
signal.signal(signal.SIGCHLD, handleSIGCHLD)

# Dualdictionary to maintain references to the objects by their PID or name
procs = Dualdict()


class RestartableProcess(object):
    """
    Due to some questionable design choices, all process names MUST be unique,
    because I keep both the name, and PID bound together in a Dualdict, which
    requires that both sets have unique key sets.  So PID's should be fine, but
    including process names might get a bit hairy.

    I liked the idea of being able to reference processes with
      restartable.procs['YOUR_PROCESS_NAME']
    instead of having to make a lookup for the name, or making the user keep
    track of the PID's themselves.

    If you have the PID still, go right ahead and reference
      restartable.procs[YOUR_PID]
    which should work just the same.

    Note... I built the Dualdict that this is built on top of, so there are
    probably some bugs somewhere ._.
    """
    def __init__(self, factory=multiprocessing.Process, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._factory = factory
        self.renew_process()

    def renew_process(self):
        self.process = self._factory(*self._args, **self._kwargs)

    def start(self):
        # cleanup the old entry in procs if we had already registered the process
        if self.process.name in procs:
            del procs[self.process.name]

        self.process.start()

        # Register the new PID and name together in the dualdict
        procs.add(self.process.pid, self.process.name, self)

    def __getattr__(self, name):
        return getattr(self.process, name)
