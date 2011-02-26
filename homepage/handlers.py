import datetime, logging
import platform

HOST = platform.uname()[1]

class DatabaseHandler(logging.Handler):
    def emit(self, record):
        from homepage.models import Log
        
        if hasattr(record, 'source'):
            source = record.source
        else:
            source = record.name

        if hasattr(record, 'request'):
            message = "%s\n\n%s" % (record.msg, repr(record.request))
        else:
            message = record.msg
        
        try:
            Log.objects.create(source=source, level=record.levelname, msg=message, host=HOST)
        except:
            # squelching exceptions sucks, but 500-ing because of a logging error sucks more
            pass
