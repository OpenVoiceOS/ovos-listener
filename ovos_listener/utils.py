import os  # Operating System functions
import re
from signal import signal, SIGKILL, SIGINT, SIGTERM, \
    SIG_DFL, default_int_handler, SIG_IGN  # signals

import pyaudio
from ovos_config.meta import get_xdg_base
from ovos_utils.file_utils import get_temp_path
from ovos_utils.log import LOG


def report_timing(ident, system, timing, additional_data=None):
    """Create standardized message for reporting timing.

    Args:
        ident (str):            identifier of user interaction
        system (str):           system the that's generated the report
        timing (stopwatch):     Stopwatch object with recorded timing
        additional_data (dict): dictionary with related data
    """
    try:
        from mycroft.metrics import report_timing
        report_timing(ident, system, timing, additional_data)
    except:
        LOG.error("Failed to upload metrics")


def find_input_device(device_name):
    """Find audio input device by name.

    Args:
        device_name: device name or regex pattern to match

    Returns: device_index (int) or None if device wasn't found
    """
    LOG.info('Searching for input device: {}'.format(device_name))
    LOG.debug('Devices: ')
    pa = pyaudio.PyAudio()
    pattern = re.compile(device_name)
    for device_index in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(device_index)
        LOG.debug('   {}'.format(dev['name']))
        if dev['maxInputChannels'] > 0 and pattern.match(dev['name']):
            LOG.debug('    ^-- matched')
            return device_index
    return None


class Signal:  # python 3+ class Signal

    """
    Capture and replace a signal handler with a user supplied function.
    The user supplied function is always called first then the previous
    handler, if it exists, will be called.  It is possible to chain several
    signal handlers together by creating multiply instances of objects of
    this class, providing a  different user functions for each instance.  All
    provided user functions will be called in LIFO order.
    """

    #
    # Constructor
    # Get the previous handler function then set the passed function
    # as the new handler function for this signal

    def __init__(self, sig_value, func):
        """
        Create an instance of the signal handler class.

        sig_value:  The ID value of the signal to be captured.
        func:  User supplied function that will act as the new signal handler.
        """
        super(Signal, self).__init__()  # python 3+ 'super().__init__()
        self.__sig_value = sig_value
        self.__user_func = func  # store user passed function
        self.__previous_func = signal(sig_value, self)
        self.__previous_func = {  # Convert signal codes to functions
            SIG_DFL: default_int_handler,
            SIG_IGN: lambda a, b: None
        }.get(self.__previous_func, self.__previous_func)

    #
    # Called to handle the passed signal
    def __call__(self, signame, sf):
        """
        Allows the instance of this class to be called as a function.
        When called it runs the user supplied signal handler than
        checks to see if there is a previously defined handler.  If
        there is a previously defined handler call it.
        """
        self.__user_func()
        self.__previous_func(signame, sf)

    #
    # reset the signal handler
    def __del__(self):
        """
        Class destructor.  Called during garbage collection.
        Resets the signal handler to the previous function.
        """
        signal(self.__sig_value, self.__previous_func)

    # End class Signal


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


#
# Create, delete and manipulate a PID file for this service
# ------------------------------------------------------------------------------
class PIDLock:  # python 3+ 'class Lock'

    """
    Create and maintains the PID lock file for this application process.
    The PID lock file is located in /tmp/mycroft/*.pid.  If another process
    of the same type is started, this class will 'attempt' to stop the
    previously running process and then change the process ID in the lock file.
    """

    #
    # Class constants
    DIRECTORY = get_temp_path(get_xdg_base())
    FILE = '/{}.pid'

    #
    # Constructor
    def __init__(self, service):
        """
        Builds the instance of this object.  Holds the lock until the
        object is garbage collected.

        service: Text string.  The name of the service application
        to be locked (ie: skills, voice)
        """
        super(PIDLock, self).__init__()  # python 3+ 'super().__init__()'
        self.__pid = os.getpid()  # PID of this application
        self.path = PIDLock.DIRECTORY + PIDLock.FILE.format(service)
        self.set_handlers()  # set signal handlers
        self.create()

    #
    # Reset the signal handlers to the 'delete' function
    def set_handlers(self):
        """
        Trap both SIGINT and SIGTERM to gracefully clean up PID files
        """
        self.__handlers = {SIGINT: Signal(SIGINT, self.delete),
                           SIGTERM: Signal(SIGTERM, self.delete)}

    #
    # Check to see if the PID already exists
    #  If it does exits perform several things:
    #    Stop the current process
    #    Delete the exiting file
    def exists(self):
        """
        Check if the PID lock file exists.  If it does
        then send a SIGKILL signal to the process defined by the value
        in the lock file.  Catch the keyboard interrupt exception to
        prevent propagation if stopped by use of Ctrl-C.
        """
        if not os.path.isfile(self.path):
            return
        with open(self.path, 'r') as L:
            try:
                os.kill(int(L.read()), SIGKILL)
            except Exception as E:
                pass

    #
    # Create a lock file for this server process
    def touch(self):
        """
        If needed, create the '/tmp/mycroft' directory than open the
        lock file for writing and store the current process ID (PID)
        as text.
        """
        if not os.path.exists(PIDLock.DIRECTORY):
            os.makedirs(PIDLock.DIRECTORY)
        with open(self.path, 'w') as L:
            L.write('{}'.format(self.__pid))

    #
    # Create the PID file
    def create(self):
        """
        Checks to see if a lock file for this service already exists,
        if so have it killed.  In either case write the process ID of
        the current service process to to the existing or newly created
        lock file in /tmp/mycroft/
        """
        self.exists()  # check for current running process
        self.touch()

    #
    # Delete the PID file - but only if it has not been overwritten
    # by a duplicate service application
    def delete(self, *args):
        """
        If the PID lock file contains the PID of this process delete it.

        *args: Ignored.  Required as this fuction is called as a signel
        handler.
        """
        try:
            with open(self.path, 'r') as L:
                pid = int(L.read())
                if self.__pid == pid:
                    os.unlink(self.path)
        except IOError:
            pass
    # End class Lock
