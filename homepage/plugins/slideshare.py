#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:
import re

from lifestream.plugins import FeedPlugin

class SlidesharePlugin(FeedPlugin):
  
  def name(self):
    return "Slideshare Feed"
  
  def pre_process(self, entry):
    super(SlidesharePlugin, self).pre_process(entry)

    # Get the flash media player url from the embed tag
    if "slideshare_embed" in entry:
        embed_match = re.search('<param name="movie" value="([^ "]*)"', entry["slideshare_embed"])
        entry["media_player_attrs"]["url"] = embed_match.group(1)
