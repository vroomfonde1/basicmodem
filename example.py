import time
from basicmodem.basicmodem import BasicModem


def callback(self, newstate):
    """Callback from modem, process based on new state"""
    if newstate == self.modem.STATE_RING:
        if self.state == self.modem.STATE_IDLE:
            att = {"cid_time": self.modem.get_cidtime(),
                   "cid_number": '',
                   "cid_name": ''}
            print('Ringing', att)
    elif newstate == self.modem.STATE_CALLERID:
        att = {"cid_time": self.modem.get_cidtime(),
               "cid_number": self.modem.get_cidnumber(),
               "cid_name": self.modem.get_cidname()}
        print('CallerID', att)
    elif newstate == self.modem.STATE_IDLE:
        print('idle')
    return

def main():
    modem = BasicModem(port='/dev/ttyACM1')
    while modem.get_response() == '':
        time.sleep(0.1)

    resp=modem.sendcmd('ATI3')

    print (resp)

    try:
        input('Wait for call, press enter to exit')
    except (SyntaxError, EOFError):
        pass

    modem.close()

if __name__ == '__main__':
    main()


