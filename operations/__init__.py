REGISTERED_OPERATIONS = { }

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

        Signature for callback methods:
        callback(progress=float, label=string)

        progress is a float [0 - 1.0].

        source: the source filename
        destination: destination filename or dirname
        parameters: a dictionary holding the parameters
        progress_callback: a callback method for progress report
        finish_callback: a callback method for achivement notification
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
        if self.progress_callback is not None:
            return self.progress_callback(progress, label)
        else:
            return True

    @staticmethod
    def parameter_values(param):
        """Return a list of possible values (list of couples) for the given parameter.

        @returns: a list of couples (value_description, value)
        """
        return []
