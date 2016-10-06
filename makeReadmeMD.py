#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import sys
import os.path
import re
from pprint import pprint
from subprocess import Popen, PIPE

readme = open('README.md', 'w')
readme.write("# Free Hack Quest 2016\n")



def getListOfDirsWithTasks():
	result = []
	dirs = os.listdir('./');
	for d in dirs:
		print(d);
		if os.path.isdir(d):
			subdirs = os.listdir('./' + d)
			subdirs.sort()
			for sd in subdirs:
				path = './' + d + '/' + sd
				if os.path.isdir(path):
					if os.path.isfile(path + '/main.json'):
						result.append(path)
						print("Found: " + path);
	return result

dirs = getListOfDirsWithTasks();
dirs.sort()

game_name = 'Free Hack Quest 2016'
stat_tasks = []
table_tasks = []
errors = {}

def append_errors(path, text):
	if path not in errors:
		errors[path] = []
	errors[path].append(text)
	

possible_categories = ["admin", "web", "pwn", "crypto", "forensic", "misc", "ppc", "recon", "reverse", "stego"]

def detectEncoding(path):
	p = Popen(['file', '-i', path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate(b"input data that is passed to subprocess' stdin")

	pattern = re.compile('.*charset=(.*).*')
	m = pattern.match(output)
	if m:
		return m.group(1)
	return 'unknown'

def parseAuthor(path):
	author = ''
	with open(path) as f:
		content = ''.join(f.readlines())
		content = content.replace('\r', '')
		content = content.replace('\n', '')
		content = content.replace('\t', '')
		pattern = re.compile('.*"nick"[ ]*\:[ ]*"([A-Z-a-z@!._]*)".*')
		m = pattern.match(content)
		if m:
			author = m.group(1)
		contacts = []
		pattern = re.compile('.*"contacts"[ ]*\:[ ]*\[[ ]*"([A-Z-a-z@/!._]*)"[ ]*,[ ]*"([A-Z-a-z@/!._]*)".*')
		m = pattern.match(content)
		if m:
			contacts.append(m.group(1));
			contacts.append(m.group(2));

	return author + '(' + ', '.join(contacts) + ')'

def appendStatCat(category, value):
	for cat in stat_tasks:
		if cat['category'] == category:
			cat['count'] = cat['count'] + 1
			cat['value'] = cat['value'] + value
			return
	stat_tasks.append({'category': category, 'count': 1, 'value': value})


def checkWriteUpFile(folder):
	path = folder + '/WRITEUP.md'
	if not os.path.isfile(path):
		append_errors(folder, 'Missing file WRITEUP.md')

def getCategoryFromTask(data, folder):
	category = 'unknown'
	if 'category' not in data:
		append_errors(folder, 'main.json: Missing field "category"')
	else:
		category = data['category']

	if category not in possible_categories:
		append_errors(folder, 'main.json: Field "category" has wrong value')
	return category;

def getStatusFromTask(data, folder):
	status = 'need verify'
	if 'status' not in data:
		append_errors(folder, 'main.json: Missing field "status"')
	else:
		status = data['status']
	return status;

def getValueFromTask(data, folder):
	value = 0
	if 'value' not in data:
		append_errors(folder, 'main.json: Missing field "value"')
	else:
		value = data['value']
		if value == 0:
			append_errors(folder, 'main.json: Task has 0 value')
	return value

def getDescriptionFromTask(data, folder):
	description = {"RU" : "", "EN": ""}
	if 'name' not in data:
		append_errors(folder, 'main.json: Missing field "name"')
	else:
		description = data['description']
		if 'RU' not in description:
			append_errors(folder, 'main.json: Missing subfield description "RU"')
		else:
			if description["RU"] == "":
				append_errors(folder, 'main.json: Empty field in description "RU"')
			
		if 'EN' not in description:
			append_errors(folder, 'main.json: Missing subfield description "EN"')
		else:
			if description["EN"] == "":
				append_errors(folder, 'main.json: Empty field in description "EN"')
	return description

def getAuthorsFromTask(data, path):
	authors = []
	if 'authors' not in data:
		append_errors(path, 'main.json: Missing field "authors"')
	else:
		
		if not isinstance(data['authors'], list):
			append_errors(path, 'main.json: Field "authors" must be list')
		else:
			authors_ = data['authors']
			
			for author in authors_:
				name = ""
				team = ""
				contacts = []
				if "name" not in author:
					append_errors(path, 'main.json: Missing subfield author "name"')
				else:
					name = author["name"]
					if name == "":
						append_errors(path, 'main.json: Subfield author "name" is empty')
						
				if "team" not in author:
					append_errors(path, 'main.json: Missing subfield author "team"')
				else:
					team = author["team"]
					if team == "":
						append_errors(path, 'main.json: Subfield author "team" is empty')
				if "contacts" not in author:
					append_errors(path, 'main.json: Missing subfield author "contacts"')
				else:
					if not isinstance(author['contacts'], list):
						append_errors(path, 'main.json: Subfield author "contacts" must be list')
					else:
						for c in author['contacts']:
							if c == "":
								append_errors(path, 'main.json: Empty field in author "contacts"')
							else:
								contacts.append(c);
				contacts = ', '.join(contacts)
				if contacts == "":
					append_errors(path, 'main.json: Missing data in subfield authors "contacts"')
				authors.append('[' + team + '] ' + name + ' (' + contacts + ')')
	return authors

def getNameFromTask(data, folder):
	name = path
	if 'name' not in data:
		append_errors(folder, 'main.json: Missing field "name"')
	else:
		name = data['name']
		if name == "":
			append_errors(folder, 'main.json: Field "name" is empty')
		dirname = folder.split("/")[-1];
		if name != dirname:
			append_errors(folder, 'main.json: Field "name" has wrong value must like dirname "' + dirname + '" be "' + folder + '"')
	return name

def getFlagKeyFromTask(data, folder):
	flag_key = ''
	if 'flag_key' not in data:
		append_errors(path, 'main.json: Missing field "flag_key"')
	else:
		flag_key = data['flag_key']
		pattern = re.compile('FHQ\(.*\)')
		pattern2 = re.compile('FHQ\{.*\}')
		m = pattern.match(flag_key)
		m2 = pattern2.match(flag_key)
		if flag_key == "":
			append_errors(folder, 'main.json: Field "flag_key" is empty')
		elif not m and not m2:
			append_errors(folder, 'main.json: Wrong value of field "flag_key" must be format "FHQ(`md5`) or FHQ(`sometext`)"')
	return flag_key
	
def getGameFromTask(data, folder):
	game = ''
	if 'game' not in data:
		append_errors(folder, 'main.json: Missing field "game"')
	else:
		game = data['game']
		if game != game_name:
			append_errors(folder, 'main.json: Wrong game name "' + game + '" Please change to "' + game_name + '"')
	return game

def getHintsFromTask(data, folder):
	hints = []
	if 'hints' not in data:
		append_errors(d, 'main.json: Missing field "hints"')
	else:
		if not isinstance(data['hints'], list):
			append_errors(d, 'main.json: Field "hints" must be list')
		else:
			hints = data['hints']
			for hint in hints:
				if 'RU' not in hint:
					append_errors(folder, 'main.json: Missing subfield hint "RU"')
				else:
					if hint["RU"] == "":
						append_errors(folder, 'main.json: Empty field in hint "RU"')
					
				if 'EN' not in hint:
					append_errors(folder, 'main.json: Missing subfield hint "EN"')
				else:
					if hint["EN"] == "":
						append_errors(folder, 'main.json: Empty field in hint "EN"')
	return hints;

for d in dirs:
	path = d + '/main.json'
	#encoding = detectEncoding(path);
	if os.path.isfile(path):
		try:
			checkWriteUpFile(d);
			
			with open(path) as main_json:
				data = json.load(main_json)
				category = getCategoryFromTask(data, d)
				value = getValueFromTask(data, d)
				status = getStatusFromTask(data, d);
				authors = getAuthorsFromTask(data, d)
				name = getNameFromTask(data, d)
				getDescriptionFromTask(data, d)
				getFlagKeyFromTask(data, d)
				appendStatCat(category, value);
				table_tasks.append({
					'category': category,
					'value': value,
					'name': name,
					'path': d,
					'status': status,
					'authors': ', '.join(authors) } )

				getGameFromTask(data, d)
				getHintsFromTask(data, d)

		except Exception:
			status = ''
			encoding = detectEncoding(path);
			if encoding != 'utf-8':
				status = encoding
				append_errors(path, 'Wrong encoding in "' + path + '", expected "utf-8", got "' + encoding + '"')
			author = parseAuthor(path);
			# print sys.exc_info()
			table_tasks.append({'category': 'unknown', 'value': 0, 'name': d, 'status': 'invalid json', 'authors': author } )
			appendStatCat('unknown', 0);

readme.write("\n## Short list of tasks\n\n")
for row in table_tasks:
	readme.write(' * ' + row['category'] + ' ' + str(row['value']) + '  "' +  row['name'] + '" by ' + row['authors'] + "\n")

if len(errors) > 0:
	readme.write("\n\n## Errors\n\n")

	for path in errors:
		print(' * ' + path)
		readme.write(' * ' + path + "\n")
		for e in errors[path]:
			print("\t * " + e)
			readme.write('\t * ' + e + "\n")


readme.write("\n## Statistics by categories\n\n")
readme.write("|Category|Count|Summary value\n")
readme.write("|---|---|---\n")

stat_tasks.sort(key=lambda x: x['category'])

tasks_count_all=0
tasks_value_all=0
for cat in stat_tasks:
	readme.write("|" + cat['category'] + "|" + str(cat['count']) + "|" + str(cat['value']) + "\n")
	tasks_count_all = tasks_count_all + cat['count'];
	tasks_value_all = tasks_value_all + cat['value'];
readme.write("|All|" + str(tasks_count_all) + "|" + str(tasks_value_all) + "\n")


# sort table
table_tasks.sort(key=lambda x: x['category'] + ' ' + str(x['value']).zfill(4))

readme.write("\n\n## Status table\n\n")
readme.write("|Category&Value|Name|Status|Author(s)\n")
readme.write("|---|---|---|---\n")

for row in table_tasks:
	readme.write('|' + row['category'] + ' ' + str(row['value']) + '|' + row['name'] + '|' + row['status'] + '|' + row['authors'] + "\n")
