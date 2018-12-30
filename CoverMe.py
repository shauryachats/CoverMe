import os
import sys
import sublime
import sublime_plugin
import threading
import subprocess
import json
import importlib

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

COVER_MODE_FILE = 'CoverMeModes.sublime-settings'

#
#	mark coverage according
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
		pid = subprocess.Popen(';'.join(self.current_mode['commands']), shell = True, stdout = subprocess.PIPE)
		stdoutput = []
		for line in pid.stdout:
			stdoutput.append(line.decode('utf-8'))
			self.set_status(line.decode('utf-8'))
		retval = pid.wait()
		if retval == 0:
			self.set_status("Tests ran successful.")
			self.cover_object = importlib.import_module('lang.' + self.current_mode['type'])
			print("cover object module: ", self.cover_object)
			coverage_data = self.cover_object.parse_coverage_file(self.current_mode['basepath'], stdoutput)
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
	def get_cover_objects(self, filename):
		with open(os.path.dirname(__file__) + '/matching.json') as f:
			matches = json.load(f)
		extension = filename.split('.')[-1]
		return [ coverobj for coverobj in matches if extension == matches[coverobj] ]

	#
	#	Gets all the options for covering to view on the quick draw bar.
	#
	def get_cover_modes(self, cover_objects):
		all_cover_modes = sublime.load_settings(COVER_MODE_FILE)
		cover_modes = []
		for cover_object in cover_objects:
			for cover_mode in all_cover_modes.get(cover_object):
				cover_mode['type'] = cover_object
				cover_modes.append(cover_mode)	
		return cover_modes

	#
	#	The magic begins here.
	#
	def run(self, edit):
		# identify file type.
		print(os.getcwd())
		cover_objects = self.get_cover_objects(self.view.file_name())
		print("cover_objects", cover_objects)
		self.cover_modes = self.get_cover_modes(cover_objects)
		print("cover_modes", self.cover_modes)
		self.draw_quick_panel()


