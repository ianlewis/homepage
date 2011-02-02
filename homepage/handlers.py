import datetime, logging
import platform

class DatabaseHandler(logging.Handler):
    def emit(self, record):
        from homepage.models import Log
        
        if hasattr(record, 'source'):
            source = record.source
        else:
            source = record.name
        
        try:
            Log.objects.create(source=source, level=record.levelname, msg=record.msg, host=HOST)
        except:
            # squelching exceptions sucks, but 500-ing because of a logging error sucks more
            pass
