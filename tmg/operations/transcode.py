#
# Copyright Olivier Aubert <contact@olivieraubert.net> 2013
#
# This software offers a media transcoding and processing platform.
#
# TMG is a free software subjected to a double license.
# You can redistribute it and/or modify if you respect the terms of either
# (at least one of both licenses):
# - the GNU Lesser General Public License as published by the Free Software Foundation;
#   either version 3 of the License, or any later version.
# - the CeCILL-C as published by CeCILL; either version 2 of the License, or any later version.
#
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
    def __init__(self, description, extension, cmdline):
        self.description = description
        self.extension = extension
        self.cmdline = cmdline

PROFILE_LIST = {
    'h264-base': Profile('H264 base profile', '.mp4', '%(handbrake)s -i "%(input)s" -f mp4 -o "%(output)s" -e x264 -x bframes=2:subme=6:mixed-refs=0:weightb=0:trellis=0:ref=4 -q 26 -E copy:aac'),
    'html5': Profile('HTML5 profile (h264 base)', '.mp4', '%(handbrake)s -i "%(input)s" -f mp4 -o "%(output)s" -e x264 -x bframes=2:subme=6:mixed-refs=0:weightb=0:trellis=0:ref=4 -q 26 -E copy:aac'),
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
        profile = PROFILE_LIST.get(self.parameters.get('profile', 'html5'))
        if profile is None:
            raise Exception("Bad profile specified")

        self.destination = self.get_tempfile(prefix='transcode', suffix=profile.extension)
        pipe = subprocess.Popen(
            shlex.split(profile.cmdline % {
                    'input': self.source,
                    'output': self.destination,
                    'handbrake':  self.find_executable('HandBrakeCLI'),
                    'ffmpeg': self.find_executable('ffmpeg'),
                    }),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True
            )
        fcntl.fcntl(
            pipe.stdout.fileno(),
            fcntl.F_SETFL,
            fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
            )
        fcntl.fcntl(
            pipe.stderr.fileno(),
            fcntl.F_SETFL,
            fcntl.fcntl(pipe.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
            )
        # Handbrake regexp:
        # Encoding: task 1 of 1, 0.96 % (289.22 fps, avg 242.52 fps, ETA 00h10m24s)
        progress_regexp = re.compile(r"""Encoding:.+?([.\d]+)\s+%""")
        eta_regexp = re.compile("ETA\s+([\d\w]+)")
        while True:
            readx = select.select([pipe.stderr.fileno()], [], [])[0]
            if readx:
                chunk = pipe.stderr.read()
                if chunk == '':
                    break
                m = progress_regexp.match(chunk)
                if m:
                    progress = 100 * float(m.group(1))
                    e = eta_regexp.match(chunk)
                    if m:
                        if self.should_continue(progress, e.group(1)) is False:
                            break
                    else:
                        if self.should_continue(progress) is False:
                            break
            time.sleep(.1)
        ret = {'output': self.destination}
        self.done(ret)
        return ret

    @staticmethod
    def parameter_values(param):
        """Return a list of possible values (list of couples) for the given parameter.

        @returns: a list of couples (value_description, value)
        """
        if param == 'profile':
            return [ (name, profile.description) for (name, profile) in PROFILE_LIST.iteritems() ]
        else:
            return []
