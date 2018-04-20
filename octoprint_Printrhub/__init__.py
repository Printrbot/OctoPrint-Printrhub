# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class PrintrhubUI(octoprint.plugin.StartupPlugin):
    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")
        

__plugin_name__ = "Printrhub"
__plugin_implementation__ = PrintrhubUI()
