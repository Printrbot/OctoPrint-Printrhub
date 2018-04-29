# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

# Plugin identifier is "Printrhub"

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin):

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")
        
    def will_handle_ui(self, request):
        return True
    
    def on_ui_render(self, now, request, render_kwargs):
        from flask import make_response, render_template
        return make_response(render_template("printrhub_web.jinja2",
                                             render_kwargs=render_kwargs))

__plugin_name__ = "Printrhub"
__plugin_implementation__ = PrintrhubUI()
