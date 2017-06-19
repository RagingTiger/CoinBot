"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: Module for managing API tokens.
"""


class ProcManager(object):
    '''
    Class to implement interface to process objects for uniformity
    '''
    # constructor
    def __init__(self):

        # init process tags
        self.tpid = None
        self.ppid = None

    def _process_exists(self, pid, attr):
        '''
        Private method to check if process exists
        '''
        # meta program
        exec('process = self.{0}'.format(pid))

        # if exists
        if process:
            exec('response = self.{0}.{1}'.format(pid, attr))
        else:
            response = None

        # respond
        return response

    def terminate(self):
        '''
        Method to wrap 'terminate()'
        '''
        return self._process_exists('ppid', 'terminate()')

    def is_alive(self):
        '''
        Method to wrap 'is_alive()'
        '''
        return self._process_exists('ppid', 'is_alive()')

    def returncode(self):
        '''
        Method to wrap 'returncode'
        '''
        return self._process_exists('tpid', 'returncode')

    def exitcode(self):
        '''
        Method to wrap 'exitcode'
        '''
        return self._process_exists('ppid', 'exitcode')

    def wait(self):
        '''
        Method to wrap 'wat()'
        '''
        self._process_exists('tpid', 'wait()')

    def join(self):
        '''
        Method to wrap 'join()'
        '''
        self._process_exists('ppid', 'join()')

    def start(self):
        '''
        Method to wrap 'start()'
        '''
        self._process_exists('ppid', 'start()')
