import json
import os
import re

line_regex = re.compile("^(?P<filename>.+):(?P<start_line>[0-9]+).(?P<start_column>[0-9]+),(?P<end_line>[0-9]+).(?P<end_column>[0-9]+) (?P<statements>[0-9]+) (?P<covered>[0-9]+)$")

def parse_coverage_file(current_mode, stdoutput):
	coverageData = {}
	with open(current_mode['basepath'] + '/cover.out', 'r') as f:
		for line in f.readlines():
			match = line_regex.match(line)
			if not match:
				continue
			matchdict = match.groupdict()

			starting_line = int(matchdict['start_line'])
			ending_line = int(matchdict['end_line'])
			file = matchdict['filename'] if matchdict['filename'].startswith('/') else current_mode['settings']['gopath'] + '/src/' + matchdict['filename']
			isCovered = "uncovered" if matchdict['covered'] == "0" else "covered"

			if file not in coverageData:
				coverageData[file] = {
					"uncovered": [],
					"covered": []
				}
			coverageData[file][isCovered].append((starting_line, ending_line))
	# Removing intersections in covered and uncovered lines.
	for file in coverageData:
		uncovered = set(coverageData[file]["uncovered"])
		covered = set(coverageData[file]["covered"])
		uncovered = uncovered - covered
		coverageData[file]["uncovered"] = list(uncovered)
		# coverageData[file]["covered"] = list(covered)
	
	for file in coverageData:
		coverageData[file] = coverageData[file]["uncovered"]
	return coverageData

