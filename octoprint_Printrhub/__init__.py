# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask # maybe clean this up.
import octoprint.filemanager.util
import subprocess

# Plugin identifier is "Printrhub"

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.BlueprintPlugin,
                  octoprint.plugin.EventHandlerPlugin):

    # note: this path /upload is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/upload
    @octoprint.plugin.BlueprintPlugin.route("/upload", methods=["POST"])
    def upload_file(self):
        """
        This section handles file uploads. If you are working on the frontend
        it may be easier and better to pass your upload to the OctoPrint API
        directly
        """

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
        # fixme: clean this up.
        for key in keys:
            param = input_name + "." + key
            if param in flask.request.values:
                result["found_file"] = True
                result[key] = flask.request.values[param]

        # grab a file handle from the temp directory where flask places it.
        # then move it over to the proper location.
        upload = octoprint.filemanager.util.DiskFileWrapper(result["name"],
                                                            result["path"])
        self._file_manager.add_file("local", result["name"],
                                    upload, allow_overwrite=True)

        # return a redirect to the main page, upload received.
        return flask.redirect(flask.url_for("index"), code=303)

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")

    def will_handle_ui(self, request):
        """
        If this function returns True, the standard OctoPrint UI is disabled.
        The plugin's UI will be drawn via on_ui_render.
        """
        # Fixme: add logic (and a toggle) to allow switching between
        # OctoPrint UI and Printrbot UI.
        return True

    def on_event(self, event, payload):
        """
        on_event allows us to hook into system events. Specifically, the
        plugin needs to know when a file is added to the system so that it
        can render an STL preview (via FauxGL)
        """

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
                # Fixme: gopath should be a config setting.
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
            css=[   "css/Printrhub.css",
                    "css/searchbar.css",
                    "css/file-browser.css",
                    "css/sidebar.css"],
            #html=[  "html/materials.html"],
            #less=["less/Printrhub.less"],
        )


    # note that these render calls can be overridden to add
    # request arguments, kwargs, etc. as part of function call.
    # see here: http://docs.octoprint.org/en/master/plugins/mixins.html#octoprint.plugin.BlueprintPlugin.get_blueprint_kwargs
    # note: this path /status is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/status
    @octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
    def render_status(self):
        """
        This is the URL that shows the printer status page.
        This is where we'll show the 'loaded' gcode file, 
        printer status, and where you start a print. 
        We may eventually want this to be default, at root, though.
        """
        from flask import make_response, render_template
        
        self._logger.info("Rendering printer status page")
        return make_response(render_template("printrhub_status.jinja2"))

    # note: this path /settings is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/settings
    @octoprint.plugin.BlueprintPlugin.route("/settings", methods=["GET"])
    def render_settings(self):
        """
        This is the URL that shows the settings.
        We'll use it to set hostname, wifi, etc. 
        """
        from flask import make_response, render_template
        
        self._logger.info("Rendering printer settings page")
        return make_response(render_template("printrhub_settings.jinja2"))

    # note: this path /materials is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/materials
    @octoprint.plugin.BlueprintPlugin.route("/materials", methods=["GET"])
    def render_materials(self):
        """
        This is the URL that shows the materials.
        We'll use it to set filament type, which will
        eventually feed into the slicer. 
        """
        from flask import make_response, render_template
        
        self._logger.info("Rendering printer materials page")
        return make_response(render_template("printrhub_materials.jinja2"))

    # note: this path /about is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/about
    @octoprint.plugin.BlueprintPlugin.route("/about", methods=["GET"])
    def render_about(self):
        """
        This is the URL that shows the about page.
        We'll use it to honor our contributors and credit 
        the software we're using to build this.
        """
        from flask import make_response, render_template
        
        self._logger.info("Rendering printer a-boot page")
        return make_response(render_template("printrhub_about.jinja2"))
    
    # No decorator needed, this renders root ("/") by default. 
    def on_ui_render(self, now, request, render_kwargs):
        """
        this is where the Printrbot UI is rendered by the plugin. Right now
        it just handles UI when the root URL is called. We can add additional
        paths (like with upload_file) that use a path decorator to add other
        UI views, or handle this as a variable passed into the request.
        """

        #self._logger.info("Calling UI_Render")
        from flask import make_response, render_template

        # Generate data for file view.
        # fixme: only needed when viewing files.
        file_data = self._file_manager.list_files()
        self._logger.info(file_data)

        # This jinja template is kept in the templates directory in the
        # plugin folder.
        return make_response(render_template("printrhub_files.jinja2",
                                             render_kwargs=render_kwargs,
                                             files=file_data))

    def bodysize_hook(self, current_max_body_sizes, *args, **kwargs):
        """
        because upload_file takes in an STL file that can get big, we need to
        override the default file size of 100k that Octoprint enforces.
        """

        # fixme: do the math and pick a reasonable size.
        return [("POST", r"/upload", 20 * 1024 * 1024)]

#    def get_template_configs(self):
#        return  [
#            dict(type="materials", custom_bindings=False)
#                ]


__plugin_name__ = "Printrhub"

def __plugin_load__():
    global __plugin_implementation__
    global __plugin_hooks__

    __plugin_implementation__ = PrintrhubUI()
    __plugin_hooks__ = {
        "octoprint.server.http.bodysize": __plugin_implementation__.bodysize_hook
    }
