from . import sound, synthizer
import wx
import config
import gui
from gui import settingsDialogs, guiHelper, NVDASettingsDialog

class SettingsPanel(gui.SettingsPanel):
	title = "Unspoken"
	def makeSettings(self, settingsSizer):
		settingsSizer = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.sayAllCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="&Disable in say all"))
		self.sayAllCheckBox.SetValue(config.conf["unspoken"]["sayAll"])
		self.speakRolesCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="&Speak object roles"))
		self.speakRolesCheckBox.SetValue(config.conf["unspoken"]["speakRoles"])
		self.HRTFCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Enable &HRTF"))
		self.HRTFCheckBox.SetValue(config.conf["unspoken"]["HRTF"])
		self.ReverbCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Enable &Reverb (Requires NVDA Restart)"))
		self.ReverbCheckBox.SetValue(config.conf["unspoken"]["Reverb"])
		self.ReverbLevelSlider = settingsSizer.addItem(wx.Slider(self, name="Reverb Level"))
		self.ReverbLevelSlider.SetValue(config.conf["unspoken"]["ReverbLevel"]*100)
		self.ReverbTimeSlider = settingsSizer.addItem(wx.Slider(self, name="Reverb Time"))
		self.ReverbTimeSlider.SetValue(config.conf["unspoken"]["ReverbTime"]*100)
		self.noSoundsCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Don't &play sounds for roles"))
		self.noSoundsCheckBox.SetValue(config.conf["unspoken"]["noSounds"])
		self.volumeCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Automatically adjust sounds with speech &volume"))
		self.volumeCheckBox.SetValue(config.conf["unspoken"]["volumeAdjust"])

	def postInit(self):
		self.sayAllCheckBox.SetFocus()

	def onSave(self):
		if self.noSoundsCheckBox.IsChecked() and not self.speakRolesCheckBox.IsChecked():
			gui.messageBox("Disabling both sounds and  speaking is not allowed. NVDA will not say roles like button and checkbox, and sounds won't play either. Please change one of these settings", "Error")
			return
		config.conf["unspoken"]["sayAll"] = self.sayAllCheckBox.IsChecked()
		config.conf["unspoken"]["speakRoles"] = self.speakRolesCheckBox.IsChecked()
		sound.context.default_panner_strategy.value=synthizer.PannerStrategy.STEREO if not config.conf['unspoken']['HRTF'] else synthizer.PannerStrategy.HRTF
		config.conf["unspoken"]["HRTF"] = self.HRTFCheckBox.IsChecked()
		config.conf["unspoken"]["Reverb"] = self.ReverbCheckBox.IsChecked()
		config.conf["unspoken"]["ReverbLevel"] = self.ReverbLevelSlider.GetValue()/100
		sound.reverb.gain.value=config.conf["unspoken"]["ReverbLevel"]
		config.conf["unspoken"]["ReverbTime"] = self.ReverbTimeSlider.GetValue()/100
		sound.reverb.t60.value=config.conf["unspoken"]["ReverbTime"]
		config.conf["unspoken"]["noSounds"] = self.noSoundsCheckBox.IsChecked()
		config.conf["unspoken"]["volumeAdjust"] = self.volumeCheckBox.IsChecked()
