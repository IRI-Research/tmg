import os
import select
import time
import subprocess
import shlex
import fcntl
import re
from . import Operation, register_operation

# Note: good reference on ffmpeg command line for h264 encoding
# http://h264.code-shop.com/trac/wiki/Encoding

class Profile(object):
    def __init__(self, description, cmdline):
        self.description = description
        self.cmdline = cmdline

PROFILE_LIST = {
    'h264-base': Profile('H264 base profile', '/usr/bin/HandBrakeCLI -i "%(input)s" -f mp4 -o "%(output)s" -e x264 -x bframes=2:subme=6:mixed-refs=0:weightb=0:trellis=0:ref=4 -q 26 -E copy:aac'),
    'html5': Profile('HTML5 profile (h264 base)', '/usr/bin/HandBrakeCLI -i "%(input)s" -f mp4 -o "%(output)s" -e x264 -x bframes=2:subme=6:mixed-refs=0:weightb=0:trellis=0:ref=4 -q 26 -E copy:aac'),
}

@register_operation(name='transcode')
class TranscodeOperation(Operation):
    """Transcode operation.
    """
    # Dictionary of parameters. Values describe the parameter type.
    # Standard parameters values can be obtainted through the parameter_values static method
    PARAMETERS = { 'profile': str }

    def start(self):
        """Start processing the file.
        """
        cmdline = PROFILE_LIST[self.parameters['profile']].cmdline
        pipe = subprocess.Popen(
            shlex.split(cmdline % { 'input': self.source, 'output': self.destination }),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True
            )
        fcntl.fcntl(
            pipe.stdout.fileno(),
            fcntl.F_SETFL,
            fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
            )
        # Handbrake regexp:
        # Encoding: task 1 of 1, 0.96 % (289.22 fps, avg 242.52 fps, ETA 00h10m24s)
        progress_regexp = re.compile(r"""Encoding:.+?([.\d]+)\s+%""")
        eta_regexp = re.compile("ETA\s+([\d\w]+)")
        while True:
            readx = select.select([pipe.stdout.fileno()], [], [])[0]
            if readx:
                chunk = pipe.stdout.read()
                if chunk == '':
                    break
                m = progress_regexp.match(chunk)
                if m:
                    e = eta_regexp.match(chunk)
                    if m:
                        if self.should_continue(m.group(1), e.group(1)) is False:
                            break
                    else:
                        if self.should_continue(m.group(1)) is False:
                            break
            time.sleep(.1)
        if self.finish_callback is not None:
            self.finish_callback()

    @staticmethod
    def parameter_values(param):
        """Return a list of possible values (list of couples) for the given parameter.

        @returns: a list of couples (value_description, value)
        """
        if param == 'profile':
            return [ (name, profile.description) for (name, profile) in PROFILE_LIST.iteritems() ]
        else:
            return []
