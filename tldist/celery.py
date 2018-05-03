from __future__ import absolute_import, unicode_literals
from celery import Celery
from configparser import ConfigParser

# Load the configuration
c = ConfigParser()
c.read('config.ini')


app = Celery('tldist',
             broker=c['processor']['celery_broker'],
             backend=c['processor']['celery_backend'],
             include=[
                 'tldist.fingerprint.task',
                 'tldist.similarity.task',
                 ]
            )

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES = 3600,
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']
)

if __name__ == '__main__':
    app.start()
