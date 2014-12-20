#! /opt/local/bin/python
from os import listdir
from os import system
from os import remove
from os.path import isfile, join, isdir
from subprocess import call
from shutil import move, copyfile

# ffmpeg -i 13-12-23.mov -vf "transpose=1" out.mp4
# ffmpeg -i out.mp4 -vf scale=-1:1080 out2.mp4
# ffmpeg -i out2.mp4 -vf pad=1920:0:656:0 out3.mp4

# load and setup configuration file
infile = open('videos.txt', 'r')
fileInfos = {}
for line in infile:
	if line.startswith('#'):
		continue
	parts = line.split('\t')
	key = parts[0].strip('\n')
	
	values = {}
	values['startTime'] = '00:00:00'
	for p in parts[1:]:
		if (p[0].isdigit()):
			values['startTime'] = p.strip('\n')
	for p in parts[1:]:
		if p.strip('\n') == 'rotate':
			values['rotate'] = '-vf "hflip,vflip"'
	for p in parts[1:]:
		if p.strip('\n') == 'darktext':
			values['darktext'] = 'black'
	for p in parts[1:]:
		if p.strip('\n') == 'transpose':
			values['transpose'] = True

	fileInfos[key] = values

files = [f for f in listdir('.') if f.endswith('.mov')]
# copy new files into 'full' folder
for f in files:
	# extract the date
	filename = f[6:14]
	# rearrange the date
	filename = filename[-2:] + '-' + filename[-5:-3] + '-' + filename[:-6] + '.mp4'
	if filename.startswith('.'):
		continue
	move(f, 'full/' + filename[:-4] + '.mov')


files = [f for f in listdir('full') if f.endswith('.mov') and not f.startswith('.')]
files.sort()

for f in files:
	filename = f[:-4]
	fullFile = 'full/' + f
	if isfile('intermediate/' + filename + '.mp4'):
		continue

	mustTranspose = False
	if filename in fileInfos:
		mustTranspose = fileInfos[filename].get('transpose', False)
	if mustTranspose:
		command = 'ffmpeg -i full/' + f + ' -vf "transpose=1" -strict experimental tmp.mp4'
		# print(command)
		system(command)
		command = 'ffmpeg -i tmp.mp4 -vf scale=-1:1080 -strict experimental tmp2.mp4'
		# print(command)
		system(command)
		command = 'ffmpeg -i tmp2.mp4 -vf pad=1920:0:656:0 -strict experimental -c:v h264 tmp3.mp4'
		# print(command)
		system(command)
		remove('tmp.mp4')
		remove('tmp2.mp4')
		fullFile = 'tmp3.mp4'

	shortFile = 'intermediate/' + filename + '.mp4'
	
	if filename in fileInfos:
		values = fileInfos[filename]
		startTime = values.get('startTime', '00:00:00').strip('\n')
		rotateArg = values.get('rotate', '').strip('\n')
	else:
		startTime = '00:00:00'
		rotateArg = ''
			
	# Create small video 
	command = 'ffmpeg -ss ' + startTime + ' -t 00:00:01 ' + \
	'-i "' + fullFile + '" -strict experimental -c:v h264 ' + rotateArg + ' "'  + shortFile + '"'
	# print(command)
	system(command)

	if mustTranspose:
		remove('tmp3.mp4')

files = [f for f in listdir('intermediate') if f.endswith('.mp4')]
files.sort()
for f in files:
	if isfile('text/' + f):
		continue
	filename = f[:-4]

	if filename in fileInfos:
		values = fileInfos[filename]
		colorArg = values.get('darktext', 'white').strip('\n')
	else:
		colorArg = 'white'

	command = 'ffmpeg -i "intermediate/' + f + '" -vf drawtext=' + \
	'"TT0001M_.TTF: text=\'' + f[0:2] + '/' + f[3:5] + '/' + \
	f[6:8] + '\': fontcolor=' + colorArg + ': fontsize=40: x=50: y=50" -codec:a copy -n ' + \
	'text/' + f
	system(command)

files = [f for f in listdir('text') if f.endswith('.mp4')]
files.sort()

blockSize = 50
nBlocks = len(files) / blockSize
for i in range(0, nBlocks):
	blockFilename = 'block-' + str(i) + '.mp4'
	if not isfile('blocks/' + blockFilename):
		low = i * blockSize
		high = (i+1) * blockSize

		blockFiles = files[low:high]

		command = 'ffmpeg '
		for f in blockFiles:
			command = command + '-i text/' + f + " "
		command = command + '-filter_complex concat=n=' + str(blockSize) + ':v=1:a=1  -strict -2 blocks/' + blockFilename
		system(command)

restFiles = files[nBlocks * blockSize:]
tmpBlockFilename = 'block-tmp.mp4'
command = 'ffmpeg '
for f in restFiles:
	command = command + '-i text/' + f + ' '
command = command + '-filter_complex concat=n=' + str(len(restFiles)) + ':v=1:a=1  -strict -2 blocks/' + tmpBlockFilename
system(command)

command = 'ffmpeg '
for i in range(0, nBlocks):
	command = command + '-i blocks/block-' + str(i) + '.mp4 '
command = command + '-i blocks/' + tmpBlockFilename + ' '
command = command + '-filter_complex concat=n=' + str(nBlocks + 1) + ':v=1:a=1  -strict -2 -y 1se.mp4'
system(command)

#remove('blocks/' + tmpBlockFilename)

copyfile('1se.mp4', '../www/alexbock.dyndns.org/html/1se.mp4')