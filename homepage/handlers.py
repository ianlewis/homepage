import datetime, logging
import platform

HOST = platform.uname()[1]

class DatabaseHandler(logging.Handler):
    def emit(self, record):
        import traceback
        from homepage.models import Log
        
        if hasattr(record, 'source'):
            source = record.source
        else:
            source = record.name

        message = record.msg

        if record.exc_info:
            exc_info = record.exc_info
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
            message = "%s\n\n%s" % (message, stack_trace)

        if hasattr(record, 'request'):
            message = "%s\n\n%s" % (message, repr(record.request))
         
        try:
            Log.objects.create(source=source, level=record.levelname, msg=message, host=HOST)
        except:
            # squelching exceptions sucks, but 500-ing because of a logging error sucks more
            pass
