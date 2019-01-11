import os
import json
import re

line_regex = re.compile("(?P<filename>[a-z.]+)( )+(?P<stmts>[0-9]+)( )+(?P<miss>[0-9]+)( )+(?P<cover>[0-9]+%)( )+(?P<missing>[0-9][0-9, -]*)")

def parse_coverage_file(current_mode, stdoutput):
	coverageData = {}
	for line in stdoutput:
		match = line_regex.match(line)
		if not match:
			continue
		matchdict = match.groupdict()
		filename = current_mode['basepath'] + '/' + matchdict['filename'] 
		coverageData[filename] = []
		missing_lines = matchdict['missing'].replace(' ','').split(',')
		for pairs in missing_lines:
			pairs = pairs.split('-')
			if len(pairs) == 1:
				pairs.append(pairs[0])
			start_line, end_line = pairs
			start_line = int(start_line)
			end_line = int(end_line)
			coverageData[filename].append((start_line, end_line))	
	return coverageData