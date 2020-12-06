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
		self.noSoundsCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Don't &play sounds for roles"))
		self.noSoundsCheckBox.SetValue(config.conf["unspoken"]["noSounds"])
		self.volumeCheckBox = settingsSizer.addItem(wx.CheckBox(self, label="Automatically adjust sounds with speech &volume"))
		self.volumeCheckBox.SetValue(config.conf["unspoken"]["volumeAdjust"])

	def postInit(self):
		self.sayAllCheckBox.SetFocus()

	def onSave(self, evt):
		if self.noSoundsCheckBox.IsChecked() and not self.speakRolesCheckBox.IsChecked():
			gui.messageBox("Disabling both sounds and  speaking is not allowed. NVDA will not say roles like button and checkbox, and sounds won't play either. Please change one of these settings", "Error")
			return
		config.conf["unspoken"]["sayAll"] = self.sayAllCheckBox.IsChecked()
		config.conf["unspoken"]["speakRoles"] = self.speakRolesCheckBox.IsChecked()
		config.conf["unspoken"]["noSounds"] = self.noSoundsCheckBox.IsChecked()
		config.conf["unspoken"]["volumeAdjust"] = self.volumeCheckBox.IsChecked()
