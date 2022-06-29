# Unspoken user interface feedback for NVDA
# By Bryan Smart (bryansmart@bryansmart.com) and Austin Hicks (camlorn38@gmail.com)
# Updated to use Synthizer by Mason Armstrong (mason@masonasons.me)

import atexit
import os
import os.path
import sys
import time
import globalPluginHandler
import NVDAObjects
import config
import speech
import controlTypes
from speech.sayAll import SayAllHandler
from logHandler import log
from . import addonGui
log.debug("Initializing Synthizer", exc_info=True)
from . import sound
import gui

from . import synthizer

UNSPOKEN_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


# Sounds

UNSPOKEN_SOUNDS_PATH = os.path.join(UNSPOKEN_ROOT_PATH, "sounds")

# Associate object roles to sounds.
sound_files={
controlTypes.ROLE_CHECKBOX : "checkbox.wav",
controlTypes.ROLE_RADIOBUTTON : "radiobutton.wav",
controlTypes.ROLE_STATICTEXT : "editabletext.wav",
controlTypes.ROLE_EDITABLETEXT : "editabletext.wav",
controlTypes.ROLE_BUTTON : "button.wav",
controlTypes.ROLE_MENUBAR : "menuitem.wav",
controlTypes.ROLE_MENUITEM : "menuitem.wav",
controlTypes.ROLE_MENU : "menuitem.wav",
controlTypes.ROLE_COMBOBOX : "combobox.wav",
controlTypes.ROLE_LISTITEM : "listitem.wav",
controlTypes.ROLE_GRAPHIC : "icon.wav",
controlTypes.ROLE_LINK : "link.wav",
controlTypes.ROLE_TREEVIEWITEM : "treeviewitem.wav",
controlTypes.ROLE_TAB : "tab.wav",
controlTypes.ROLE_TABCONTROL : "tab.wav",
controlTypes.ROLE_SLIDER : "slider.wav",
controlTypes.ROLE_DROPDOWNBUTTON : "combobox.wav",
controlTypes.ROLE_CLOCK: "clock.wav",
controlTypes.ROLE_ANIMATION : "icon.wav",
controlTypes.ROLE_ICON : "icon.wav",
controlTypes.ROLE_IMAGEMAP : "icon.wav",
controlTypes.ROLE_RADIOMENUITEM : "radiobutton.wav",
controlTypes.ROLE_RICHEDIT : "editabletext.wav",
controlTypes.ROLE_SHAPE : "icon.wav",
controlTypes.ROLE_TEAROFFMENU : "menuitem.wav",
controlTypes.ROLE_TOGGLEBUTTON : "checkbox.wav",
controlTypes.ROLE_CHART : "icon.wav",
controlTypes.ROLE_DIAGRAM : "icon.wav",
controlTypes.ROLE_DIAL : "slider.wav",
controlTypes.ROLE_DROPLIST : "combobox.wav",
controlTypes.ROLE_MENUBUTTON : "button.wav",
controlTypes.ROLE_DROPDOWNBUTTONGRID : "button.wav",
controlTypes.ROLE_HOTKEYFIELD : "editabletext.wav",
controlTypes.ROLE_INDICATOR : "icon.wav",
controlTypes.ROLE_SPINBUTTON : "slider.wav",
controlTypes.ROLE_TREEVIEWBUTTON: "button.wav",
controlTypes.ROLE_DESKTOPICON : "icon.wav",
controlTypes.ROLE_PASSWORDEDIT : "editabletext.wav",
controlTypes.ROLE_CHECKMENUITEM : "checkbox.wav",
controlTypes.ROLE_SPLITBUTTON : "splitbutton.wav",
}

sounds = dict() # For holding instances in RAM.

#taken from Stackoverflow. Don't ask.
def clamp(my_value, min_value, max_value):
	return max(min(my_value, max_value), min_value)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(addonGui.SettingsPanel)
		config.conf.spec["unspoken"]={
			"sayAll" : "boolean(default=False)",
			"speakRoles" : "boolean(default=False)",
			"noSounds" : "boolean(default=False)",
			"HRTF" : "boolean(default=True)",
			"volumeAdjust" : "boolean(default=True)",
			"Reverb" : "boolean(default=True)",
			"ReverbLevel" : "float(default=1.0)",
			"ReverbTime" : "float(default=0.2)",
		}
		log.debug("Creating Synthizer context", exc_info=True)
		sound.reverb.filter_input.value=synthizer.BiquadConfig.design_identity()
		sound.reverb.gain.value=config.conf['unspoken']['ReverbLevel']
		sound.reverb.mean_free_path.value=0.01
		sound.reverb.t60.value=config.conf['unspoken']['ReverbTime']
		sound.reverb.late_reflections_delay.value=0
#We don't want it changing the volume of sounds that are far away from the listening point (The center of the screen).
		log.debug("Setting Synthizer context distance model to NONE", exc_info=True)
		sound.context.default_panner_strategy.value=synthizer.PannerStrategy.STEREO if not config.conf['unspoken']['HRTF'] else synthizer.PannerStrategy.HRTF
		sound.context.default_distance_model.value = synthizer.DistanceModel.NONE
		self.make_sound_objects()
		# Hook to keep NVDA from announcing roles.
		self._NVDA_getSpeechTextForProperties = speech.speech.getPropertiesSpeech
		speech.speech.getPropertiesSpeech = self._hook_getSpeechTextForProperties
		self._previous_mouse_object = None
		self._last_played_object = None
		self._last_played_time = 0
		#these are in degrees.
		self._display_width = 180.0
		self._display_height_min = -40.0
		self._display_height_magnitude = 50.0

	def make_sound_objects(self):
		"""Makes sound objects from synthizer."""
		log.debug("Creating Synthizer sound objects", exc_info=True)
		for key, value in sound_files.items():
			path = os.path.join(UNSPOKEN_SOUNDS_PATH, value)
			sound_object = sound.sound3d("3d",sound.context)
			log.debug("Loading "+path, exc_info=True)
			sound_object.load(path)
			if config.conf["unspoken"]["Reverb"]==True: sound.context.config_route(sound_object.source, sound.reverb)
			sounds[key] = sound_object

	def shouldNukeRoleSpeech(self):
		if config.conf["unspoken"]["sayAll"] and SayAllHandler.isRunning():
			return False
		if config.conf["unspoken"]["speakRoles"]:
			return False
		return True

	def _hook_getSpeechTextForProperties(self, reason=NVDAObjects.controlTypes.OutputReason.QUERY, *args, **kwargs):
		role = kwargs.get('role', None)
		if role:
			if (role in sounds and self.shouldNukeRoleSpeech()):
				#NVDA will not announce roles if we put it in as _role.
				kwargs['_role'] = kwargs['role']
				del kwargs['role']
		return self._NVDA_getSpeechTextForProperties(reason, *args, **kwargs)

	def _compute_volume(self):
		if not config.conf["unspoken"]["volumeAdjust"]:
			return 1.0
		driver=speech.speech.getSynth()
		volume = getattr(driver, 'volume', 100)/100.0 #nvda reports as percent.
		volume=clamp(volume, 0.0, 1.0)
		return volume if not config.conf['unspoken']['HRTF'] else volume+0.25

	def play_object(self, obj):
		if config.conf["unspoken"]["noSounds"]:
			return
		curtime = time.time()
		if curtime-self._last_played_time < 0.1 and obj is self._last_played_object:
			return
		self._last_played_object = obj
		self._last_played_time = curtime
		role = obj.role
		if role in sounds:
			# Get coordinate bounds of desktop.
			desktop = NVDAObjects.api.getDesktopObject()
			desktop_max_x = desktop.location[2]
			desktop_max_y = desktop.location[3]
			# Get location of the object.
			if obj.location != None:
				# Object has a location. Get its center.
				obj_x = obj.location[0] + (obj.location[2] / 2.0)
				obj_y = obj.location[1] + (obj.location[3] / 2.0)
			else:
				# Objects without location are assumed in the center of the screen.
				obj_x = desktop_max_x / 2.0
				obj_y = desktop_max_y / 2.0
			# Scale object position to audio display.
			angle_x = ((obj_x-desktop_max_x/2.0)/desktop_max_x)*self._display_width
			#angle_y is a bit more involved.
			percent = (desktop_max_y-obj_y)/desktop_max_y
			angle_y = self._display_height_magnitude*percent+self._display_height_min
			#clamp these to Libaudioverse's internal ranges.
			angle_x = clamp(angle_x, -90.0, 90.0)
			angle_y = clamp(angle_y, -90.0, 90.0)
			#In theory, this can be made faster if we remember which is last, but that shouldn't matter here
			for i, j in sounds.items():
				j.stop()
			sounds[role].generator.playback_position.value = 0.0
			sounds[role].source.position.value = (angle_x, angle_y, 0)
			sounds[role].source.gain.value=self._compute_volume()
			sounds[role].play()

	def event_becomeNavigatorObject(self, obj, nextHandler, isFocus=False):
		self.play_object(obj)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		self.play_object(obj)
		nextHandler()

	def event_mouseMove(self, obj, nextHandler, x, y):
		if obj != self._previous_mouse_object:
			self._previous_mouse_object = obj
			self.play_object(obj)
		nextHandler()

	def terminate(self):
		synthizer.shutdown()