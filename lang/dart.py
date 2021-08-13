import os
import json

def resolve_uri(uri, package_dir):
	"""
	Given package:project/path/to/file.dart, returns:
	C:\\path\\to\\project\\lib\\path\\to\\file.dart
	(Windows only)
	"""
	file = uri [uri.find("/") + 1:]
	path = package_dir + "\\lib\\" + file.replace("/", "\\")	

def parse_coverage_file(current_mode, stdoutput): 
	# Assumes tests were run with:
	# dart test --coverage=test/coverage
	package_dir = current_mode["basepath"]
	package_name = package_dir.split("\\") [-1]
	coverage_dir = package_dir + "\\test\\coverage\\test"
	coverage_files = os.listdir(coverage_dir)

	# Data is returned in JSON files.
	# Each file contains JSON objects, one for each file
	# Each file has: 
	# - "source": URI of the file (see below)
	# - "hits": list of numbers
	# 
	# Dart URIs are of the form: package:project/path/to/file.dart
	# We need to resolve it into a full-fledged file path.
	# We use the variables set above to do so.
	# 
	# "hits" is one-dimensional, but it's actually arranged in pairs.
	# Each pair is (line_number, times_line_was_run)
	# CoverMe doesn't need the latter, so we filter it out.

	result = {}
	for cov_file in coverage_files:
		# Load the file
		filename = coverage_dir + "\\" + cov_file
		with open(filename) as file: 
			contents = json.load(file)

		# Read the JSON file
		for entry in contents ["coverage"]:
			# There are many irrelevant files in the coverage report. 
			if ("package:" + package_name) not in entry["source"]: continue

			uri = entry["source"]
			hits = entry["hits"]
			path = resolve_uri(uri, package_dir)
			if path not in result: result[path] = []

			# Line numbers are every *other* element
			for index in range(0, len(hits), 2):  
				line = hits[index]
				if line not in result[path]: result[path].append(line)

	# CoverMe expects to have line *ranges*, but we only have line numbers
	return {
		file: [
			(line, line + 1) for line in result[file]
		]
		for file in result
	}

	return result
