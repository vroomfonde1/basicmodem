"""
A simple modem implementation that supports caller ID.

For more details about this platform, please refer to the documentation at
https://github.com/vroomfonde1/basicmodem
"""
import logging

_LOGGER = logging.getLogger(__name__)
DEFAULT_PORT = '/dev/ttyACM0'
DEFAULT_CMD_CALLERID = 'AT+VCID=1'


class BasicModem(object):
    """Implementation of simple modem"""
    STATE_IDLE = 'idle'
    STATE_RING = 'ring'
    STATE_CALLERID = 'callerid'

    def __init__(self, port=DEFAULT_PORT, incomingCallNotificationFunc=None):
        """Initialize internal variables"""
        import serial
        import threading
        self.port = port
        self.incomingCallNotificationFunc = incomingCallNotificationFunc or self._placeHolderCallback
        self._state = self.STATE_IDLE
        self.cmd_callerid = DEFAULT_CMD_CALLERID
        self.cmd_response = ''
        self.cmd_responselines = []
        self.cid_time = 0
        self.cid_name = ''
        self.cid_number = ''
        self.ser = None

        _LOGGER.debug('Opening port %s', self.port)
        try:
            self.ser = serial.Serial(port=self.port)
        except serial.SerialException:
            _LOGGER.error('Unable to open port %s', self.port)
            self.ser = None
            return

        if self.write(self.cmd_callerid) == True:
            threading.Thread(target=self._modem_sm, daemon=True).start()

    def write(self, cmd='AT'):
        """write string to modem"""
        self.cmd_response = ''
        self.cmd_responselines = []
        import serial
        try:
            cmd += '\r\n'
            self.ser.write(cmd.encode())
        except serial.SerialException:
            _LOGGER.error('Unable to write to port %s', self.port)
            return False
        return True

    def sendcmd(self, cmd='AT', timeout=1.0):
        """send command, waiting for response"""
        import time
        if self.write(cmd):
            while self.get_response() == '' and timeout > 0:
                time.sleep(0.1)
                timeout-=0.1
        return self.get_lines()

    def _placeHolderCallback(self, *args):
        """ Does nothing """
        _LOGGER.debug('called with args: {0}'.format(args))
        return

    def set_state(self, state):
        """Set the state."""
        self._state = state
        return

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def get_cidname(self):
        return self.cid_name

    @property
    def get_cidnumber(self):
        return self.cid_number

    @property
    def get_cidtime(self):
        return self.cid_time

    def get_response(self):
        return self.cmd_response

    def get_lines(self):
        return self.cmd_responselines

    def close(self):
        """close modem port, exit worker thread"""
        if self.ser:
            self.ser.close()
            self.ser = None
        return

    def _modem_sm(self):
        """Handle modem response state machine."""
        import serial
        import datetime
        RING_TIMEOUT = 10
        RING_WAIT = None
        ring_timer = RING_WAIT

        while self.ser:
            self.ser.timeout = ring_timer
            try:
                resp = self.ser.readline()
            except serial.SerialException:
                _LOGGER.error('Unable to read from port %s', self.port)
                break
            except SystemExit:
                return

            if self.state != self.STATE_IDLE and len(resp) == 0:
                ring_timer = RING_WAIT
                self.set_state(self.STATE_IDLE)
                self.incomingCallNotificationFunc(self.state)
                continue

            resp = resp.decode()
            resp = resp.strip('\r\n')
            if self.cmd_response == '':
                self.cmd_responselines.append(resp)
            _LOGGER.debug('mdm: %s', resp)
            if resp == '':
                continue

            if resp in ['OK', 'ERROR']:
                self.cmd_response = resp
                continue

            if resp in ['RING']:
                if self.state == self.STATE_IDLE:
                    self.cid_name = ''
                    self.cid_number = ''
                    self.cid_time = datetime.datetime.now()

                self.set_state(self.STATE_RING)
                self.incomingCallNotificationFunc(self.state)
                ring_timer = RING_TIMEOUT
                continue

            if len(resp) <= 4:
                continue

            if resp.find('=') == -1:
                continue

            ring_timer = RING_TIMEOUT
            cid_field, cid_data = resp.split('=')
            cid_field = cid_field.strip()
            cid_data = cid_data.strip()
            if cid_field in ['DATE']:
                self.cid_time = datetime.datetime.now()
                continue

            if cid_field in ['TIME']:
                continue

            if cid_field in ['NMBR']:
                self.cid_number = cid_data
                continue

            if cid_field in ['NAME']:
                self.cid_name = cid_data
                self.set_state(self.STATE_CALLERID)
                self.incomingCallNotificationFunc(self, self.state)
                _LOGGER.debug('CID: %s %s %s',
                              self.cid_time.strftime("%I:%M %p"),
                              self.cid_name,
                              self.cid_number)
                self.write(self.cmd_callerid)
                continue

            continue

        _LOGGER.debug('Exiting modem state machine')
        return
