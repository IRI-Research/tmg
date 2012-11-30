from celery.decorators import task
from celery.utils.log import get_task_logger

from tmg.models import Process

logger = get_task_logger(__name__)

@task
def start_process(pid, callback=None):
    proc = Process.objects.get(pk=pid)
    logger.info("Starting process %s" % proc)

    try:
        logger.info("------ running %s" % proc)
        #proc.start()
    except Exception, exc:
        logger.info("Failed process %s" % proc)
        #start_process.retry(exc=exc, countdown=60)

    logger.info("Finished process %s" % proc)
    if callback:
        subtask(callback).delay(proc.pk)
