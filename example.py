"""Example: monitor for incoming calls and display caller id information."""

from basicmodem.basicmodem import BasicModem as bm

state = bm.STATE_IDLE


def callback(newstate):
    """Callback from modem, process based on new state"""
    print('callback: ', newstate)
    if newstate == modem.STATE_RING:
        if state == modem.STATE_IDLE:
            att = {"cid_time": modem.get_cidtime,
                   "cid_number": modem.get_cidnumber,
                   "cid_name": modem.get_cidname}
            print('Ringing', att)
    elif newstate == modem.STATE_CALLERID:
        att = {"cid_time": modem.get_cidtime,
               "cid_number": modem.get_cidnumber,
               "cid_name": modem.get_cidname}
        print('CallerID', att)
    elif newstate == modem.STATE_IDLE:
        print('idle')
    return


def main():
    global modem
    modem = bm(port='/dev/ttyACM0', incomingcallback=callback)

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
    except (SyntaxError, EOFError, KeyboardInterrupt):
        pass

    modem.close()


if __name__ == '__main__':
    main()
