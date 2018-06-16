# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask # maybe clean this up.
import octoprint.filemanager.util
import subprocess

import base64
import rsa

# Plugin identifier is "Printrhub"

class PrintrhubUI(octoprint.plugin.StartupPlugin,
                  octoprint.plugin.SettingsPlugin,
                  octoprint.plugin.UiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.BlueprintPlugin,
                  octoprint.plugin.EventHandlerPlugin):

#    def __init__(self):
#        # Fixme: maybe this is unnecessary and gets removed.
#        # Test what happens when the PrintrhubUI setting is manually
#        # removed from the config.yaml file.
#        #self._PrintrhubUI = True
#        pass

#    def get_settings_defaults(self):
#        """
#        Default settings for the Printrhub UI Plugin.
#        These are loaded by default when the plugin is first installed
#        or when the system is re-initialized.
#        ""
#        Note: I removed this because it was obliterating the settings
#        need to research more.
#
#        return dict(
#            PrintrhubUI=True
#        )

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

        upload_name = flask.request.values.get("file.name", None)
        upload_path = flask.request.values.get("file.path", None)

        # grab a file handle from the temp directory where flask places it.
        # then move it over to the proper location.

        # Fixme: some error checking wouldn't hurt here.
        upload = octoprint.filemanager.util.DiskFileWrapper(upload_name,
                                                            upload_path)

        self._file_manager.add_file("local", upload_name,
                                    upload, allow_overwrite=True)

        # return a redirect to the main page, upload received.
        return flask.redirect(flask.url_for("index"), code=303)


    @octoprint.plugin.BlueprintPlugin.route("/toggleUI", methods=["GET", "POST"])
    def toggle_UI(self):
        """
        Turn the Printrhub UI on or off.
        """
        if self._PrintrhubUI == True:
            self._PrintrhubUI = False
        else:
            self._PrintrhubUI = True

        # Fixme: the settings aren't getting written to config.yaml.
        self._settings.set_boolean(["PrintrhubUI"], False)
        return flask.redirect(flask.url_for("index"), code=303)

    def on_startup(self, host, port):
        self._PrintrhubUI = self._settings.get(["PrintrhubUI"])


    # Fixme: These are merges from Kelly's UI work (WIP stuff)
    # Brian/Kelly to discuss and implement.

#    @octoprint.plugin.BlueprintPlugin.route("/show/<filename>", methods=["GET"])
#    def get_uploaded_file(filename):
#        from flask import render_template
#
#        filename = '/static/img/' + filename + ".png"
#        return make_response(render_template('get_uploaded_file.jinja2', filename=filename))
#
#    @octoprint.plugin.BlueprintPlugin.errorhandler(404)
#    def image_not_found(error):
#        from flask import render_template
#
#        self._logger.info("*** 404 image_not_found ***")
#        return make_response(render_template('noimage_thumb.jinja2'), 404)

    def on_after_startup(self):
        self._logger.info("Printrhub UI successfully running.")

    def will_handle_ui(self, request):
        """
        If this function returns True, the standard OctoPrint UI is disabled.
        The plugin's UI will be drawn via on_ui_render.
        """
        # Fixme: this only controls UI for 'root' URL. If the user tries to
        # open one of the other, deeper links, they still render (for now)
        return self._PrintrhubUI

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

                ''' Kelly's Path'''
                env = {'GOPATH': r'/home/pi/go'}
                my_result = subprocess.check_output("/usr/local/go/bin/go run " + script_path + " --input " + stl_path + " --output " + out_path,
                                                    shell=True,
                                                    stderr=subprocess.STDOUT,
                                                    env=env)
                '''

                env = {'GOPATH': r'/home/pi/gocode'}
                my_result = subprocess.check_output("go run " + script_path + " --input " + stl_path + " --output " + out_path,
                                                    shell=True,
                                                    stderr=subprocess.STDOUT,
                                                    env=env)
'''
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
                    "css/sidebar.css",
                    "css/create-material-button.css",
                    "css/table.css"],
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

        printer_data = self._printer.get_current_data()

        """
        Most of these values are NoneType when no print is in progress

        Printer state format:
          progress:
            completion:
            filepos:
            printTime:
            printTimeLeft:
            printTimeOrigin:
          state:
            text:             // Human readable printer state
            flags:
              cancelling:     // Bool
              paused:         // Bool
              operational:    // Bool
              pausing:        // Bool
              printing:       // Bool
              sdReady:        // Bool
              error:          // Bool
              ready:          // Bool
              closedOrError:  // Bool
            currentZ:
            job:
              estimatedPrintTime:
              filament:
                volume:
                length:
              file:
                date:
                origin:
                size:
                name:
                path:
              lastPrintTime:
              offsets:
        """

        self._logger.info("Rendering printer status page")
        #self._logger.info(printer_data)
        return make_response(render_template("printrhub_status.jinja2",
                                             printer_data=printer_data))

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
    @octoprint.plugin.BlueprintPlugin.route("/minifactory", methods=["GET"])
    def render_minifactory(self):
        """
        This is the URL that shows the about page.
        We'll use it to honor our contributors and credit
        the software we're using to build this.
        """
        from flask import make_response, render_template

        self._logger.info("Rendering Minifactory Page")
        return make_response(render_template("printrhub_minifactory.jinja2"))

    # note: this path /about is relative to the plugin root,
    # so it is located at ./plugin/Printrhub/about
    @octoprint.plugin.BlueprintPlugin.route("/thingiverse", methods=["GET"])
    def render_thingiverse(self):
        """
        This is the URL that shows the about page.
        We'll use it to honor our contributors and credit
        the software we're using to build this.
        """
        from flask import make_response, render_template

        self._logger.info("Rendering Thingiverse Page")
        return make_response(render_template("printrhub_thingiverse.jinja2"))

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
