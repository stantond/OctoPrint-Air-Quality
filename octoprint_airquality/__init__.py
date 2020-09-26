# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import flask
import octoprint.plugin
from octoprint.server import user_permission
from . import DatabaseManager, SensorsManager

class AirqualityPlugin(octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.TemplatePlugin,
					   octoprint.plugin.StartupPlugin,
					   octoprint.plugin.EventHandlerPlugin,
					   octoprint.plugin.SimpleApiPlugin):

	# supportedSensors = {
	# 	"Plantower PMS5003": "5003",
	# 	"Plantower PMS7003": "7003",
	# 	"Plantower PMSA003": "A003"
	# }

	def on_after_startup(self):
		self.database_manager = DatabaseManager.DatabaseManager(self)
		self.sensors_manager = SensorsManager.SensorsManager(self)
	# 	if self.sensors_manager.is_connected():
	# 		self._logger.info("Sensors are alive!")
	# 	else:
	# 		self._logger.error("Could not find the sensors.")

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			sensor_port="/dev/ttyUSB0",
			sensor_baud_rate="9600",
			arrDevices = []
		)

	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=True)
		]

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/jquery-ui.min.js","js/knockout-sortable.js","js/ko.observableDictionary.js","js/airquality.js"],
			css=["css/airquality.css"],
			less=["less/airquality.less"]
		)

	##~~ EventHandlerPlugin mixin

	def on_event(self, event, payload):
		if event == "Connected":
			try:
				self.sensors_manager.refresh_sensors(payload["port"])
			except AttributeError:
				# As this event also fires for a connection during start-up,
				# `sensor_manager` may not exist yet, so we can safely catch
				# and ignore this error.
				pass

	##~~ SimpleApiPlugin mixin

	def get_api_commands(self):
		return dict(
			refresh_sensors=[]
		)

	def on_api_command(self, command, data):
		if not user_permission.can():
			return flask.make_response("User does not have permission", 403)
		self._logger.info(command)
		if command == "refresh_sensors":
			try:
				self.sensors_manager.refresh_sensors()
				return flask.make_response('{"message": "Sensors refreshed"}', 200)
			except:
				return flask.make_response('{"message": "Failed to refresh sensors"}', 500)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			airquality=dict(
				displayName="Air Quality Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="stantond",
				repo="OctoPrint-AirQuality",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/stantond/OctoPrint-AirQuality/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Air Quality Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = AirqualityPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

