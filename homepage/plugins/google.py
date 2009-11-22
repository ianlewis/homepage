#:coding=utf-8:

from lifestream.plugins import FeedPlugin

from datetime import datetime

class GooglePlugin(FeedPlugin):
  
    def name(self):
        return "Google Reader Feed"

    def pre_process(self, entry):
        super(GooglePlugin,self).pre_process(entry)
        entry["published"] = datetime.now()
