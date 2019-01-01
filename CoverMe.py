import os
import sys
import sublime
import sublime_plugin
import threading
import subprocess
import json
import importlib

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

SETTINGS_FILE = 'CoverMe.sublime-settings'
COVER_MODE_FILE = 'CoverMeModes.sublime-settings'

#
#	Mark coverage according to the coverage data returned from the cover object.
#
def mark_coverage(view, coverage_data):
	current_file = sublime.active_window().active_view().file_name()
	regions = []
	marker = 'markup.deleted'
	for starting_line, ending_line in coverage_data[current_file]:
		for line_number in range(starting_line - 1, ending_line):
			region = view.full_line(view.text_point(line_number, 0))
			regions.append(region)
	view.add_regions('CoverMe', regions, marker, "dot", sublime.HIDDEN)

def erase_coverage(view):
	view.erase_regions('CoverMe')
	
class CoverMe(sublime_plugin.TextCommand):
	def set_status(self, strng):
		print("CoverMe: " + strng)
		self.view.set_status("CoverMe", "CoverMe: " + strng)

	def run_tests(self):
		self.set_status("Running tests for " + self.current_mode['type'])
		os.chdir(self.current_mode['basepath'])
		# Add environment variables
		print(self.settings.get('go'))
		env = os.environ.copy()
		for key in self.current_mode['settings']:
			env[key] = self.current_mode['settings'][key]

		pid = subprocess.Popen(';'.join(self.current_mode['commands']), shell = True, env = env, stdout = subprocess.PIPE)
		stdoutput = []
		for line in pid.stdout:
			stdoutput.append(line.decode('utf-8'))
			self.set_status(line.decode('utf-8'))
		retval = pid.wait()
		if retval == 0:
			self.set_status("Tests ran successful.")
			self.cover_object = importlib.import_module('lang.' + self.current_mode['type'])
			print("cover object module: ", self.cover_object)
			coverage_data = self.cover_object.parse_coverage_file(self.current_mode, stdoutput)
			print("coverage_data", coverage_data)
			mark_coverage(self.view, coverage_data)
		else:
			self.set_status("Tests failed with return code " + str(retval))

	def draw_quick_panel(self):
		items = [[ mode['type'] + ": " + mode['title'], ';'.join(mode['commands']) ] for mode in self.cover_modes ]
		sublime.active_window().show_quick_panel(items, self.quick_panel_callback)

	#
	#	Make a lambda.
	#
	def quick_panel_callback(self, arg):
		print(arg)
		if arg == -1:
			return 
		erase_coverage(self.view)
		self.current_mode = self.cover_modes[arg]
		if 'basepath' not in self.current_mode:
			self.current_mode['basepath'] = os.path.dirname(self.view.file_name())
		# Start test running on a non blocking thread.
		thread = threading.Thread(target = self.run_tests)
		thread.start()

	#
	#	Gets the respective cover objects according to the file extension.
	#
	def get_raw_cover_modes(self, filename):
		self.settings = sublime.load_settings(SETTINGS_FILE)
		matches = self.settings.get('matching')
		extension = filename.split('.')[-1]
		cover_objects = [ coverobj for coverobj in matches if extension == matches[coverobj] ]
		all_cover_modes = sublime.load_settings(COVER_MODE_FILE)
		
		return {
			cover_object: all_cover_modes.get(cover_object) for cover_object in cover_objects
		}

	#
	#	Process cover modes into drawable selection panel
	#
	def process_raw_cover_modes(self, cover_objects):
		cover_modes = []
		for cover_object in cover_objects:
			for cover_mode in cover_objects[cover_object]:
				cover_mode['type'] = cover_object
				cover_mode['settings'] = self.settings.get(cover_object)
				cover_modes.append(cover_mode)	
		return cover_modes

	#
	#	The magic begins here.
	#
	def run(self, edit):
		# check if project file is present, import cover modes from it.
		project_file = sublime.active_window().active_view().settings()
		if project_file.has('CoverMe'):
			self.raw_cover_modes = project_file.get('CoverMe')
		# else load default cover modes according to file extension.
		else:
			self.raw_cover_modes = self.get_raw_cover_modes(self.view.file_name())
		print("raw_cover_modes", self.raw_cover_modes)
		self.cover_modes = self.process_raw_cover_modes(self.raw_cover_modes)
		# Draw cover mode selection panel
		self.draw_quick_panel()
