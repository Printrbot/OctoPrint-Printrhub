# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask # maybe clean this up.
import octoprint.filemanager.util
import subprocess

# Plugin identifier is "Printrhub"
# Fixme: 1MB file is too large for the system.

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.BlueprintPlugin,
                  octoprint.plugin.EventHandlerPlugin):

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

        # this is for debugging purposes, but I use the variables below.
        for key in keys:
            param = input_name + "." + key
            if param in flask.request.values:
                result["found_file"] = True
                result[key] = flask.request.values[param]

        # grab a file handle from the temp directory where flask places it.
        # then move it over to the proper location.
        # fixme: make overwriting the default behavior.
        upload = octoprint.filemanager.util.DiskFileWrapper(result["name"],
                                                            result["path"])
        self._file_manager.add_file("local", result["name"],
                                    upload, allow_overwrite=True)

        # fixme: replace this with a redirect to the main page. 
        return flask.jsonify(result)

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")
        
    def will_handle_ui(self, request):
        return True

    def on_event(self, event, payload):
        # this appears to be the best place to hook into the
        # system when a file is uploaded.
        if event == "FileAdded":
            self._logger.info("*** A FILE WAS UPLOADED ***")
            #self._logger.info(payload)
            stl_path = self._file_manager.path_on_disk(payload["storage"],
                                                       payload["path"])
            self._logger.info(stl_path)
            # not sure if static folder is better than datafolder,
            # but using the static folder for now.
            out_path = self._basefolder + "/static/img/" + payload["path"] + ".png"
            self._logger.info(out_path)
            script_path = self._basefolder + "/stl_preview.go"
            self._logger.info(script_path)
            my_result = ""
            try: 
                # fixme: this is dangerous and hacked.
                # dangerous: running as shell.
                # hacked: manually putting in gopath.
                env = {'GOPATH': r'/home/pi/gocode'}
                my_result = subprocess.check_output("go run " + script_path + " --input " + stl_path + " --output " + out_path,
                                                    shell=True,
                                                    stderr=subprocess.STDOUT,
                                                    env=env)
            except subprocess.CalledProcessError as e:
                self._logger.info ("something went wrong")
                my_result = e.output
                self._logger.info(e.output)
                self._logger.info(e.cmd)
                self._logger.info(e.returncode)
                
            self._logger.info(my_result)
            
    def get_assets(self):
        # fixme: before making "prod" commit, change config yaml
        # to bundle, and check in CSS files. 
        return dict(
            css=["css/Printrhub.css"],
            less=["less/Printrhub.less"]
        )
    
    def on_ui_render(self, now, request, render_kwargs):
        #self._logger.info("Calling UI_Render")
        from flask import make_response, render_template

        # Generate data for file view.
        # fixme: only needed when viewing files.
        file_data = self._file_manager.list_files()
        self._logger.info(file_data)

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
