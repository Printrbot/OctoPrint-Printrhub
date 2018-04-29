# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

# Plugin identifier is "Printrhub"

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.AssetPlugin):

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")
        
    def will_handle_ui(self, request):
        return True

    def get_assets(self):
        # fixme: before making "prod" commit, change config yaml
        # to bundle, and check in CSS files. 
        return dict(
            css=["css/Printrhub.css"],
            less=["less/Printrhub.less"]
        )
    
    def on_ui_render(self, now, request, render_kwargs):
        from flask import make_response, render_template
        return make_response(render_template("printrhub_web.jinja2",
                                             render_kwargs=render_kwargs))

__plugin_name__ = "Printrhub"
__plugin_implementation__ = PrintrhubUI()
