"""Example: monitor for imcoming calls and display caller id information."""

from basicmodem.basicmodem import BasicModem as bm

state = bm.STATE_IDLE


def callback(bm, newstate):
    """Callback from modem, process based on new state"""
    print('callback: ', newstate)
    if newstate == bm.STATE_RING:
        if state == bm.STATE_IDLE:
            att = {"cid_time": bm.get_cidtime,
                   "cid_number": bm.get_cidnumber,
                   "cid_name": bm.get_cidname}
            print('Ringing', att)
    elif newstate == bm.STATE_CALLERID:
        att = {"cid_time": bm.get_cidtime,
               "cid_number": bm.get_cidnumber,
               "cid_name": bm.get_cidname}
        print('CallerID', att)
    elif newstate == bm.STATE_IDLE:
        print('idle')
    return


def main():
    modem = bm(port='/dev/ttyACM1', incomingcallback=callback)

    if modem.state == modem.STATE_FAILED:
        print('Unable to initialize modem, exiting.')
        return 

    """Print modem information."""
    resp = modem.sendcmd('ATI3')
    for line in resp:
        if line:
            print(line)

    try:
        input('Wait for call, press enter to exit')
    except (SyntaxError, EOFError):
        pass

    modem.close()


if __name__ == '__main__':
    main()
