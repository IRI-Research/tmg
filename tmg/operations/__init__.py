import os
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

REGISTERED_OPERATIONS = { }

def list_registered_operations():
    return [ (name, kl.__doc__.splitlines()[0]) for (name, kl) in REGISTERED_OPERATIONS.iteritems() ]

# Register decorator
def register_operation(name=None):
    """Register an operation.

    name: the operation name
    """
    def register(klass):
        REGISTERED_OPERATIONS[name] = klass
        klass._registered_name = name
        return klass
    if name is None:
        raise Exception("Error: an operation name must be provided")
    if name in REGISTERED_OPERATIONS:
        raise Exception("Error: overwriting previous registered operation %s" % name)
    return register

class Operation(object):
    """Generic operation.
    """
    # Dictionary of parameters. Values describe the parameter type.
    # Standard parameters values can be obtainted through the parameter_values static method
    PARAMETERS = {}

    def __init__(self, source=None, destination=None, parameters=None, progress_callback=None, finish_callback=None):
        """Instanciation

        If destination is None, then the Operation is in charge of
        generating a default one.

        Signature for callback methods:
        callback(progress=float, label=string)
        where progress is a float [0 - 1.0].

        @param source: the source filename
        @type source: a string (path)
        @param destination: destination filename or dirname
        @type destination: a string (path)
        @param parameters: a dictionary holding the parameters
        @type parameters: dict
        @param progress_callback: a callback method for progress report
        @type progress_callback: a method with the signature callback(progress=float, label=string)
        @param finish_callback: a callback method for achievement notification
        @type finish_callback: a method
        """
        self.source = source
        self.destination = destination
        self.parameters = parameters or {}
        self.progress_callback = progress_callback
        self.finish_callback = finish_callback

    def start(self):
        """Start processing the file.
        """
        pass

    def should_continue(self, progress, label=None):
        """Progress report and abort function.

        If this method returns False, the process should be aborted.
        """
        self.log("Progress", progress, label)
        if self.progress_callback is not None:
            return self.progress_callback(progress, label)
        return True

    @staticmethod
    def parameter_values(param):
        """Return a list of possible values (list of couples) for the given parameter.

        @returns: a list of couples (value_description, value)
        """
        return []

    def log(self, *p):
        """Log a message.
        """
        logger.info(u"%s: %s" % (unicode(self.__class__).split('.')[-1], "\n".join(unicode(n) for n in p)))

def load_modules():
    """Load all operation modules.
    """
    d = os.path.dirname(os.path.realpath(__file__))
    for name in os.listdir(d):
        base, ext = os.path.splitext(name)
        if ext == '.py' and not name.startswith('_'):
            # A potential module
            logger.info("Importing %s from %s" % (base, d))
            __import__('.'.join((__name__, base)))
            #fullname = os.path.join(d, name)
            #with open(fullname, 'r') as f:
            #    imp.load_source('.'.join( (__name__, name) ), fullname, f)
