# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask # maybe clean this up.
import octoprint.filemanager.util

# Plugin identifier is "Printrhub"

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.BlueprintPlugin):

    @octoprint.plugin.BlueprintPlugin.route("/upload", methods=["POST"])
    def upload_file(self):
        self._logger.info("File upload page")

        # fixme: understand why this call requires an API key
        # (and then ignores the actual value)
        input_name = "file"
        keys = ("name", "size", "content_type", "path")

        result = dict(
            found_file=False,
        )

        # prove to ourselves that the file object doesn't exist
        # like flask says it should. 
        if 'file' not in flask.request.files:
            result["status"] = "No file found"
        else:
            result["status"] = "Found a file"
            
        for key in keys:
            param = input_name + "." + key
            if param in flask.request.values:
                result["found_file"] = True
                result[key] = flask.request.values[param]


        upload = octoprint.filemanager.util.DiskFileWrapper(result["name"], result["path"])
        self._file_manager.add_file("local", result["name"], upload)

        
        return flask.jsonify(result)

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
        self._logger.info("Calling UI_Render")
        self._logger.info(request.path)
        self._logger.info(request.method)

        from flask import make_response, render_template

        # Generate data for file view.
        # fixme: only needed when viewing files.
        file_data = self._file_manager.list_files()
        #self._logger.info(file_data)

        return make_response(render_template("printrhub_web.jinja2",
                                             render_kwargs=render_kwargs,
                                             files=file_data))

    def bodysize_hook(self, current_max_body_sizes, *args, **kwargs):
        # fixme: do the math and pick a reasonable size.
        return [("POST", r"/upload", 1024 * 1024)]
    

__plugin_name__ = "Printrhub"
# __plugin_implementation__ = PrintrhubUI()

def __plugin_load__():
    global __plugin_implementation__
    global __plugin_hooks__

    __plugin_implementation__ = PrintrhubUI()
    __plugin_hooks__ = {
        "octoprint.server.http.bodysize": __plugin_implementation__.bodysize_hook
    }
