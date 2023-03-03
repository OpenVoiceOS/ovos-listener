import re

import pyaudio

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
