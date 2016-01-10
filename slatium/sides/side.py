import multiprocessing


class Side(multiprocessing.Process):
    def recieve(self, channel, username, message):
        self.ipc_queue.put(('message_recieve', [self.side_name, username, message]))

    def deliver(self, channel, username, message):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()
