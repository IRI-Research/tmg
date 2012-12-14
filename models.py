from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from fields import JSONField
from django.contrib.auth.models import User
import tmg.operations as operations
from celery.task.control import revoke

class Process(models.Model):
    """Representation of a process.
    """
    class Meta:
        verbose_name_plural = "Processes"
        ordering = ('status', 'created_on')
        get_latest_by = 'created_on'

    # FIXME: see matching data in celery API (status + ETA)
    CREATED = 'created'
    STARTED = 'started'
    CANCELLING = 'cancelling'
    FINISHED = 'finished'
    CANCELLED = 'cancelled'
    ABORTED = 'aborted'
    STATUS_CHOICES = (
        (CREATED, 'Created'),
        (STARTED, 'Started'),
        (CANCELLING, 'Cancelling'),
        (FINISHED, 'Finished'),
        (CANCELLED, 'Cancelled'),
        (ABORTED, 'Aborted'),
        )

    # Principle: a process will store its result (transcoded file,
    # data files such as shot list in JSON format, etc) in a directory
    # named from the task_id. Upon completion, it will keep the
    # results there, waiting for the user to copy/move the information
    # somewhere else. The operation returns the location of its
    # output, and some details about it (filename, or set of files,
    # etc)
    # A periodic task will cleanup old cached results.

    owner = models.ForeignKey(User, related_name='processes')

    # We do not use a FileField here since we store here server-side filenames
    source = models.FilePathField(max_length=1024,
                                  path=settings.MEDIA_ROOT,
                                  recursive=True,
                                  help_text='Source filename for the operation')

    # id of the operation (transcode, shotdetect, etc)
    operation = models.CharField(max_length=255, help_text='Operation class identifier', choices=[ (name, kl.__doc__.splitlines()[0]) for (name, kl) in operations.REGISTERED_OPERATIONS ])
    task_id = models.CharField(max_length=255, editable=False)

    created_on = models.DateTimeField(null=True, editable=False, auto_now=True, help_text='Process created on')
    started_on = models.DateTimeField(null=True, editable=False, help_text='Process started on')
    finished_on = models.DateTimeField(null=True, editable=False, help_text='Process finished on')
    status = models.CharField(max_length=32,
                              editable=False,
                              default=CREATED,
                              choices=STATUS_CHOICES,
                              help_text="Process status")
    progress = models.IntegerField(blank=True,
                                   editable=False,
                                   default=0,
                                   help_text="Progress information [0..100]")
    eta = models.CharField(blank=True,
                           editable=False,
                           max_length=255,
                           help_text='Estimated Time of Achievement')

    # Operation-specific parameters
    parameters = JSONField(blank=True)

    def current_status(self):
        if self.status == self.CREATED:
            return "not yet started"
        elif self.status == self.STARTED:
            return "started on %s" % self.started_on
        elif self.status == self.CANCELLING:
            return "cancelling"
        elif self.status == self.CANCELLED:
            return "cancelled on %s" % self.finished_on
        elif self.status == self.FINISHED:
            return "finished on %s" % self.finished_on

    def __unicode__(self):
        return u"Operation %s pk=%s on %s: %s" % (self.operation,
                                                  self.pk, self.source, self.current_status())

    def save(self, *p, **kw):
        super(Process, self).save(*p, **kw)
        # Start the process
        # Putting the import here works around the circular dependency
        if self.status == self.CREATED:
            # Start the process
            from tasks import start_process
            task = start_process.delay(self.pk)

    def delete(self, *p, **kw):
        """Cancelling an operation.

        It will not delete the resource itself, rather put it in the
        CANCELLING (then CANCELLED) state.
        """
        self.status = self.CANCELLING
        self.save()
        # Cancel the task
        if self.task_id:
            revoke(self.task_id, terminate=True)
        else:
            raise Exception("No associated task")

    def start(self):
        """Start the process.
        """
        op = operations.REGISTERED_OPERATIONS[self.operation](source=self.source,
                                                              destination=None,
                                                              parameters=self.parameters,
                                                              progress_callback=None,
                                                              finish_callback=None)
        op.start()
