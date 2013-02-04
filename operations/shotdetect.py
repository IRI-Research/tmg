import os
import sys
import select
import time
import subprocess
import tempfile
import fcntl
import re
from . import Operation, register_operation

@register_operation(name='shotdetect')
class ShotdetectOperation(Operation):
    """Shotdetect operation.
    """
    # Dictionary of parameters. Values describe the parameter type.
    # Standard parameters values can be obtained through the parameter_values static method
    PARAMETERS = { 'sensitivity': int }

    def start(self):
        """Start processing the file.
        """
        self.tempdir = unicode(tempfile.mkdtemp('', 'shotdetect'), sys.getfilesystemencoding())
        args = [ "/usr/bin/shotdetect", 
                '-i', self.source.encode('utf8'),
                '-o', self.tempdir.encode('utf8'),
                '-s', str(self.parameters.get('sensitivity', 60)) ]
        self.log("Starting", *args)
        pipe = subprocess.Popen(
            args,
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
        # Shotdetect regexp:
        progress_regexp = re.compile(r"""Shot log :: (\d+)""")
        self.log("Entering loop")
        while True:
            readx = select.select([pipe.stderr.fileno()], [], [])[0]
            if readx:
                chunk = pipe.stderr.read()
                if chunk == '':
                    break
                m = progress_regexp.match(chunk)
                if m and self.should_continue(m.group(1)) is False:
                    self.log("Breaking loop")
                    break
            # FIXME: active waiting is bad
            time.sleep(.1)
        if self.finish_callback is not None:
            self.finish_callback()

    @staticmethod
    def parameter_values(param):
        """Return a list of possible values (list of couples) for the given parameter.

        @returns: a list of couples (value_description, value)
        """
        if param == 'sensitivity':
            return [ ("Standard", 70),
                     ("Less sensitive", 50),
                     ("More sensitive", 80) ]
        else:
            return []
