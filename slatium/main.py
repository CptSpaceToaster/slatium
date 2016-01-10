import multiprocessing
import slatium


"""
def thingy(arg1):
    print('proc: starting')
    time.sleep(arg1)
    print('proc: deading')
"""


def main():
    """
    p1 = slatium.RestartableProcess(name='proc1', target=thingy, args=(1,))
    p2 = slatium.RestartableProcess(name='proc2', target=thingy, args=(4,))
    print('main: inited procs')
    p1.start()
    p2.start()
    print('main: started a proc: {0}'.format(p1.pid))
    print('main: started a proc: {0}'.format(p2.pid))

    while(1):
        pass
    """
    host_pipe, slack_pipe = multiprocessing.Pipe()
    print(cmds)

    p = slatium.RestartableProcess(name='slack', target=slatium.SlackSide, args=('xoxb-14766807600-AgenL9nrFmnTtGgJ8W81HuUX', 30))

    p.start()
    # idle until needs_exit
    # needs_exit.wait()

    # All commands will come in as a tuple: ('type', ['arg', 'arg', 'arg'])
    #   ('add_channel', ['side_name' 'channel_name', 1])
    #   ('remove_channel', ['side_name', 'channel_name', 1])
    #   ('message_recieve, ['side_name', 'channel_name', 'user', 'message']')
    #   ('alias_user, ['side_name', 'user', 'destination_side_name', 'user_alias']')

    # cleanup
    """
    for name, side in sides.items():
        if side.is_alive:
            print('Closing: {0}'.format(side))
            side.close()
    """
