import sublime, sublime_plugin, subprocess, os, threading

# For ST3
def plugin_loaded():
	global sett
	sett = sublime.load_settings("PublishProject.sublime-settings")

class PublishProject(sublime_plugin.EventListener):
	def on_post_save_async(self, view):
		self.publish('onSave')

	def publish(self, publishType):
		publishSettings = sett.get(publishType)
		if not publishSettings == None:
			settings = publishSettings.get('projects')
			project = sublime.active_window().project_file_name()

			if not project == None:
				projectData = sublime.active_window().project_data()
				projectName = os.path.splitext(os.path.basename(project))[0]
				projectDir = os.path.dirname(project)
				projectFolders = projectData['folders']

				if not settings == None:
					for path in settings.keys():
						commands = settings.get(path).get('commands')
						excludes = settings.get(path).get('exclude')
						if projectName == path and len(commands) > 0:
							print("Publish project '" + publishType + "'")
							for command in commands:
								for projectFolder in projectFolders:
									folderPath = projectFolder.get('path')
									if not os.path.isabs(folderPath):
										folderPath = os.path.join(projectDir,folderPath)
									if not self.isExcluded(excludes, folderPath):
										p = subprocess.Popen([command, folderPath], stdout=subprocess.PIPE)
										out, err = p.communicate()
										print (out.decode('utf-8'))
										if not err == None:
											print (err.decode('utf-8'))

	def isExcluded(self, excludes, item):
		if not excludes == None:
			for excluded in excludes:
				if excluded in item:
					print(item + " is excluded")
					return True

		return False

class PublishProjectCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		thread = PublishThread('onPublish')
		thread.start()

		self.handle_thread(thread)

	def handle_thread(self, thread):
		next_thread = None
		if(thread.isAlive()):
			next_thread = thread

		if not next_thread == None:
			sublime.set_timeout(lambda: self.handle_thread(next_thread))
			return

		sublime.status_message('Publish complete')

class PublishThread(threading.Thread):
	def __init__(self, publishType):
		self.publishType = publishType
		threading.Thread.__init__(self)

	def run(self):
		proj = PublishProject()
		proj.publish(self.publishType)
