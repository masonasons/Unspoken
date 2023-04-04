from . import sound, synthizer
import wx
import config
import gui
from gui import settingsDialogs, guiHelper, NVDASettingsDialog

class SettingsPanel(gui.SettingsPanel):
	title = "Unspoken"
	def makeSettings(self, settingsSizer):
		settingsSizer = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.sayAllCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="&Play sounds during say all"))
		self.sayAllCheckBox.SetValue((True if config.conf["unspoken"]["sayAll"]==False else False))
		self.speakRolesCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="&Speak object roles"))
		self.speakRolesCheckBox.SetValue(config.conf["unspoken"]["speakRoles"])
		self.HRTFCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Use &HRTF (3D Sound)"))
		self.HRTFCheckBox.SetValue(config.conf["unspoken"]["HRTF"])
		self.ReverbCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Use &Reverb (Requires NVDA Restart)"))
		self.ReverbCheckBox.SetValue(config.conf["unspoken"]["Reverb"])
		self.ReverbLevelSliderLabel = settingsSizer.addItem(wx.StaticText(self, label="Reverb Level"))
		self.ReverbLevelSlider = settingsSizer.addItem(wx.Slider(self))
		self.ReverbLevelSlider.SetValue(config.conf["unspoken"]["ReverbLevel"]*100)
		self.ReverbTimeSliderLabel = settingsSizer.addItem(wx.StaticText(self, label="Reverb Time"))
		self.ReverbTimeSlider = settingsSizer.addItem(wx.Slider(self))
		self.ReverbTimeSlider.SetValue(config.conf["unspoken"]["ReverbTime"]*100)
		self.noSoundsCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="&play sounds for roles (Enable Add-On)"))
		self.noSoundsCheckBox.SetValue((True if config.conf["unspoken"]["noSounds"]==False else False))
		self.volumeCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Automatically adjust sounds with speech &volume"))
		self.volumeCheckBox.SetValue(config.conf["unspoken"]["volumeAdjust"])

	def postInit(self):
		self.sayAllCheckBox.SetFocus()

	def onSave(self):
		if not self.noSoundsCheckBox.IsChecked() and not self.speakRolesCheckBox.IsChecked():
			gui.messageBox("Disabling both sounds and  speaking is not allowed. NVDA will not say roles like button and checkbox, and sounds won't play either. Please change one of these settings", "Error")
			return
		config.conf["unspoken"]["sayAll"] = not self.sayAllCheckBox.IsChecked()
		config.conf["unspoken"]["speakRoles"] = self.speakRolesCheckBox.IsChecked()
		sound.context.default_panner_strategy.value=synthizer.PannerStrategy.STEREO if not config.conf['unspoken']['HRTF'] else synthizer.PannerStrategy.HRTF
		config.conf["unspoken"]["HRTF"] = self.HRTFCheckBox.IsChecked()
		config.conf["unspoken"]["Reverb"] = self.ReverbCheckBox.IsChecked()
		config.conf["unspoken"]["ReverbLevel"] = self.ReverbLevelSlider.GetValue()/100
		sound.reverb.gain.value=config.conf["unspoken"]["ReverbLevel"]
		config.conf["unspoken"]["ReverbTime"] = self.ReverbTimeSlider.GetValue()/100
		sound.reverb.t60.value=config.conf["unspoken"]["ReverbTime"]
		config.conf["unspoken"]["noSounds"] = not self.noSoundsCheckBox.IsChecked()
		config.conf["unspoken"]["volumeAdjust"] = self.volumeCheckBox.IsChecked()
