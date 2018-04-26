# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

# Ok, let's make sense out of the naming convention:
# Plugin folder is "filetab"
# Plugn name is not set explicitly.
# Plugin implementation/function is FiletabPlugin()
# Tab callout in config.yaml is plugin_filetab
# Jinja template name is "filetab_tab.jinja2"

# in my case, plugin folder is Octorprint-Printrhub
# Plugin name is "Printrhub"


class PrintrhubUI(octoprint.plugin.StartupPlugin, octoprint.plugin.UiPlugin, octoprint.plugin.TemplatePlugin):

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")

    def will_handle_ui(self, request):
        return False

    def get_template_configs(self):
        return [
            dict(type="tab", name="Files", template="printrhub_tab.jinja2")
        ]
    
    def on_ui_render(self, now, request, render_kwargs):
        from flask import make_response, render_template
        #self._logger.info("Keywords  %s", % str(render_kwargs.keys())
        return make_response(render_template("printrhub_web.jinja2",
                                             **render_kwargs))
                          
__plugin_name__ = "Printrhub"
__plugin_implementation__ = PrintrhubUI()
