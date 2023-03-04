# This class is a singleton that will track the number and time of calls to LGL.  This is necessary because
# LGL currently has a limit of 300 calls every 5 minutes.  This class will track the number of calls and when
# that count nears the threshold, it will pause up to 5 minutes from the call at the beginning of the threshold.

import logging
import time

CALL_THRESHOLD = 299
WAIT_PERIOD = 305

log = logging.getLogger()

class LglCallTracker:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LglCallTracker, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._call_count = 0  # This is the number of calls since the last reset
        self._times = []  # This will contain a list of the times calls were made

    # This method will clear the call counter.
    def clear_call_count(self):
        self._call_count = 0

    # This method will add the current time to the time stack
    def push_time(self):
        self._times.append(int(time.time()))

    # Find the time that has elapsed since the current call.  This is done by looking at the call made
    # CALL_THRESHOLD calls ago and seeing if WAIT_PERIOD seconds have passed.
    #
    # Returns - the number of seconds since the current call
    def elapsed_time(self):
        current_index = len(self._times) - 1
        first_index = current_index - CALL_THRESHOLD
        if first_index < 0:
            first_index = 0
        elapsed_time = self._times[current_index] - self._times[first_index]
        log.debug('The elapsed time since the current call is {}.'.format(elapsed_time))
        return elapsed_time

    # This method will increment the number of calls and add the current time to the time stack.
    # It will also check if the number of calls is over the threshold and wait WAIT_PERIOD minutes if
    # that is the case.
    #
    # Side effects: A delay may be inserted because too many calls have been made.
    def increment_call_count(self):
        self._call_count += 1
        self.push_time()
        log.debug('The call count is {}.'.format(self._call_count))
        if self._call_count > CALL_THRESHOLD:
            elapsed = self.elapsed_time()
            if elapsed < WAIT_PERIOD:
                wait_time = WAIT_PERIOD - elapsed
                log.info('More than {} calls to LGL have been made in the last {} '.format(CALL_THRESHOLD, elapsed)
                         + 'seconds.  This will  exceed the number of calls allowed by LGL in {} '.format(WAIT_PERIOD)
                         + 'seconds and will cause an error.  There will be a {} second delay '.format(wait_time)
                         + 'until the program resumes to avoid this error.')
                time.sleep(wait_time)
                self.clear_call_count()
                log.info('The program is resuming now.')
