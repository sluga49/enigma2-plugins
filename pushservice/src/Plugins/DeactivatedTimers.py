#######################################################################
#
#    Push Service for Enigma-2
#    Coded by betonme (c) 2012 <glaserfrank(at)gmail.com>
#    Support: http://www.i-have-a-dreambox.com/wbb2/thread.php?threadid=167779
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#######################################################################

# Config
from Components.config import ConfigYesNo, NoSave

# Plugin internal
from Plugins.Extensions.PushService.__init__ import _
from Plugins.Extensions.PushService.PluginBase import PluginBase

# Plugin specific
import NavigationInstance
from time import localtime, strftime

SUBJECT = _("Found deactivated timer(s)")
BODY    = _("Deactivated timer list:\n%s")
TAG     = _("DeactivatedTimerPushed")


class DeactivatedTimers(PluginBase):
	
	ForceSingleInstance = True
	
	def __init__(self):
		# Is called on instance creation
		PluginBase.__init__(self)
		self.timers = []
		
		# Default configuration
		self.setOption( 'remove_timer', NoSave(ConfigYesNo( default = False )), _("Remove deactivated timer(s)") )

	def run(self):
		# Return Header, Body, Attachment
		# If empty or none is returned, nothing will be sent
		# Search deactivated timers
		self.timers = []
		text = ""
		for timer in NavigationInstance.instance.RecordTimer.timer_list + NavigationInstance.instance.RecordTimer.processed_timers:
			if timer.disabled and TAG not in timer.tags:
				text += str(timer.name) + "    " \
							+ strftime(_("%Y.%m.%d %H:%M"), localtime(timer.begin)) + " - " \
							+ strftime(_("%H:%M"), localtime(timer.end)) + "    " \
							+ str(timer.service_ref and timer.service_ref.getServiceName() or "") \
							+ "\n"
				self.timers.append( timer )
		if self.timers and text:
			return SUBJECT, BODY % text
		else:
			return None

	# Callback functions
	def success(self):
		# Called after successful sending the message
		if self.getValue('remove_timer'):
			# Remove deactivated timers
			for timer in self.timers[:]:
				if timer in NavigationInstance.instance.RecordTimer.processed_timers:
					NavigationInstance.instance.RecordTimer.processed_timers.remove(timer)
				elif timer in NavigationInstance.instance.RecordTimer.timer_list:
					NavigationInstance.instance.RecordTimer.timer_list.remove(timer)
				self.timers.remove(timer)
		else:
			# Set tag to avoid resending it
			for timer in self.timers[:]:
				timer.tags.append(TAG)
				NavigationInstance.instance.RecordTimer.saveTimer()
				self.timers.remove(timer)

	def error(self):
		# Called after message sent has failed
		self.timers = []