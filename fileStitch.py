#!/usr/bin/python

############################
# Name:	   fileStitch.py
# Author:  Stephan Gross
# Date:	   07/08/2013
# Purpose: Is used to try and piece together files in 'file carving' challenges. These \
#	   challenges usually give you a file that has been cut into multiple pieces, \
#	   and it is your job to put them together in the correct order.
#
# Note: Currently this program only works for zip files, and picture files \
#	(png, jpg, gif, bmp).
#
#To-Do list:
#	allow user to specify the order of other files
#	add other command line arguments?
############################

#import argparse
import itertools
import time
import subprocess
import sys
import timeit
import re
import string
import os
import shutil

######################
#Function Definitions#
######################

# Function: askFirstFile
# Purpose: Ask the user if they know the first file
# Parameters: none
# Returns: answer if user knows the first file
def askFirstFile(): 
	answer = raw_input("Enter the name of the first file.\nIf you don't know the first file, leave it blank: ")
	return answer

# Function: askLastFile
# Purpose: Ask the user if they know the last file
# Parameters: none
# Returns: answer if user knows the last file
def askLastFile():
	answer = raw_input("\nEnter the name of the last file.\nIf you don't know the last file, leave it blank: ")
	return answer

# Function: askFileType
# Purpose: Ask the user if they know the file type we need to piece together
# Parameters: none
# Returns: answer if user knows the file type
def askFileType():
	my_bool = True

	while my_bool == True:
		print "Enter the # of the file type from the menu below.\n"
		print "#   File Type"
		print "-------------"
		print "1   zip"
		print "2   picutre (gif,png,jpg,bmp)"
		print "3   tiff (experimental)\n"
	
		answer = int(raw_input("choice: "))

		if answer != 1 and answer != 2 and answer != 3:
			print "Error, invalid choice. Try again."
		else:
			my_bool = False

	return answer

#Function: determineFileType
#Purpose: Try to automatically determine the file type based on the \
#	  hex header of the files. This also tells us which file is \
#	  the first file.
#Parameters: top_dir = the directory containing the files to piece together 
#Returns: 'zip' = if it's a zip file
#	  'picture' = if it's a picture file (jpg,bmp,gif,png)
#	  aFile = the file name containing the header, hence the first file
#	  None, None = if we couldn't find a header
def determineFileType(top_dir):
	print('Trying to determine the file type and the first file...')
	for aFile in os.listdir(top_dir):
		if aFile == 'myTmp':
			continue
		file_path = top_dir + aFile
		p1 = subprocess.Popen(['hexdump', '-n', '6', file_path], stdout=subprocess.PIPE)
		p2 = subprocess.Popen(['awk', '{if(NR == 1){print $2,$3,$4;}}'], stdin=p1.stdout, stdout=subprocess.PIPE)
		hex_header = p2.communicate()[0]
		hex_header = hex_header.rstrip()

		if re.match(zip_file_reg_ex, hex_header):
			print('\tWe matched a zip file header.\n')
			return 'zip', aFile
		elif re.match(picture_file_reg_ex, hex_header):
			print('\tWe matched a picture file header.\n')
			return 'picture', aFile

	return None, None #We didn't find a file type, return None, None

#Function: determineLastFile
#Purpose: Try to determine the last file base on the file size.
#Parameters: top_dir = the directory containing the files to piece together
#Returns: smallest_file = the file with the smallest size in bytes, which is generally the last file
#	  None = if there is no single smallest file
def determineLastFile(top_dir):
	# The last file is usually the smallest one in size
	smallest_size = 0
	smallest_file = ''
	counter = 0
	same_counter = 0

	print('Trying to dertmine the last file...')

	file_list, list_length = createList(None, None, top_dir)
	for aFile in file_list:
		stat_info = os.lstat(top_dir + aFile)
		if counter == 0:
			smallest_size = stat_info.st_size
			smallest_file = aFile
			counter += 1
			continue

		if stat_info.st_size < smallest_size:
			smallest_size = stat_info.st_size
			smallest_file = aFile
			same_counter = 0 # Reset counter to 0 since we just \
					 # found new smallest file.
		elif stat_info.st_size == smallest_size:
			# Files matching the smallest size exist. This means \
			# we cannot be sure what the last file is when basing \
			# it on file size. Use the  same_counter in case we \
			# haven't gone through all files in the list yet.
			same_counter += 1

	if same_counter == 0:
		# Only one file is has the smallest size
		print('\tFound the last file.\n')
		return smallest_file
	else:
		# Multiple files have the samllest size, can't be sure which \
		# one is the last file.
		return None
			
#Function: createList
#Purpose: create the list of all the files
#Parameters: fileBeg = The first file of the sequence (can be empty)
#	     fileEnd = The last file of the sequence (can be empty)
#	     top_dir = The directory containing the files to piece together
#Returns: theList = The list of all the files to be processed
#	  listLen = Length of the list (the number of files to be processed)
def createList(fileBeg, fileEnd, top_dir):
	if top_dir:
		#Get a list of all items in the top_dir directory
		the_list = os.listdir(top_dir)

	if 'fileStitch.py' in the_list:
		#Remove our script from the list
		the_list.remove('fileStitch.py')
	if 'myTmp' in the_list:
		#Remove the temp directory from the list
		the_list.remove('myTmp')

	if fileBeg:
		the_list.remove(fileBeg)
	
	if fileEnd:
		the_list.remove(fileEnd)

	list_len=len(the_list)
	return the_list, list_len

#Function: createLocalList
#Purpose: create the local list
#Parameters: permList = A permutation of the initial list of files
#	     fileBeg = The first file of the sequence (can be empty)
#	     fileEnd = The last file of the sequence (can be empty)
#Returns: initList = The permutated list with the beginning and/or last files in proper position
def createLocalList(permList,fileBeg,fileEnd):
	initList=[]

	if fileBeg:
		initList.append(fileBeg) #Place the first file at the beggining

	#Add each item in order of the current permutation to initList
	for item in (permList):
		initList.append(item)
		
	if fileEnd:
		initList.append(fileEnd) #Place last file at end

	return initList

#Function: printFileOrder
#Purpose: Once the file has been pieced together successfully, this will print the \
#	  order of the files to the screen and to a file.
#Parameters: the_list = the list of files in the appropriate order
#	     out_file_path = the full path to the file we will write the order to
#Returns: Nothing
def printFileOrder(the_list, out_file_path):
        count=1

        print "The order of the files are: "
        out_file=open(out_file_path, "w")

        for aFile in (the_list):
                print str(count) + ') ' + aFile
                out_file.write(str(count) + ') ' + aFile + '\n')
                count+=1

        out_file.close()

#Function: zipFile
#Puprose: Run commands necessary to piece together a zip file
#Parameters: start_file = first file
#	     end_file = last file
#	     top_dir = directory containing files to piece together
#Returns: nothing
def zipFile(start_file, end_file, top_dir):
	count = 0
	file_list, list_len = createList(start_file, end_file, top_dir)

	#Calculate all of the different permutations and test
	for aPermutation in itertools.permutations(file_list,list_len):
		count += 1
		print('Trying permutation ' + str(count))
		local_list=createLocalList(aPermutation,start_file,end_file)

		#Cat all files in order of this permutation
		for aFile in (local_list):
			cmd = 'cat ' + top_dir + aFile + ' >> ' + top_dir + 'myTmp/test.zip'
			subprocess.call(cmd,shell=True)
	
		#Try to unzip the file		
		returnCode = subprocess.call('unzip ' + top_dir + 'myTmp/test.zip -d ' + top_dir + 'myTmp/testing/ >/dev/null 2>&1',shell=True)
	
		#If returnCode is not 0 then it is an error, so we delete all 
		#of the files so that we can try again.
		if returnCode != 0:
			subprocess.call('rm -f ' + top_dir + 'myTmp/test.zip ' + top_dir + 'myTmp/testing/*',shell=True)
		else:
			print "\nLooks like the zip file was pieced together successfully."
			print "The zip file can be found here: " + top_dir + 'myTmp/test.zip'
			print "The zip file order can be found here: " + top_dir + 'fileOrder.txt'
			print "The extracted zip archive can be found here: " + top_dir + 'myTmp/testing/\n'
			printFileOrder(local_list, top_dir + 'fileOrder.txt')
			break

#Function choosePicFileFunc
#Purpose: Chooses the appropriate picture file function to use based on the number \
#	  of files that need to be pieced together.
#Parameters: top_dir = the directory containing the files to piece together
#Returns: 'inefficient' = if there are 4 or less files to piece together
#	  'efficient' = if there are more than 4 files to piece together
def choosePicFileFunc(top_dir):
	file_list = os.listdir(top_dir)
	if len(file_list) <= 4:
		return 'inefficient'
	else:
		return 'efficient'

#Function: inefficientPicFile
#Puprose: Run commands necessary to piece together a picture file
#Parameters: start_file = first file
#	     end_file = last file
#	     top_dir = directory containing the files to piece together
#Returns: nothing
def inefficientPicFile(start_file, end_file, top_dir):
	files_list, list_length = createList(start_file, end_file, top_dir)
	my_bool = True
	count = 0

	while my_bool:
		for aPermutation in itertools.permutations(files_list,list_length):
			count += 1
			print('Trying permutation ' + str(count))
			local_list=createLocalList(aPermutation,start_file,end_file)
		
			#Cat all files in order of this permutation
			for aFile in (local_list):
				cmd = 'cat ' + top_dir + aFile + ' >> ' + top_dir + 'myTmp/testPic'
				subprocess.call(cmd,shell=True)
			subprocess.call('eog ' + top_dir + 'myTmp/testPic 2>/dev/null', shell=True)

			answer=string.strip(raw_input("Was this the proper order? (y|n|q): "))
			if re.search('[qQ]|[qQ][uU][iI][tT]', answer):
				print('Quitting at request of user. Please delete temporary directories and any files created by this script in ' + top_dir + ' before attempting to run this script again.\n')
				sys.exit(0)
			elif re.search('[yY]|[yY][eE][sS]', answer):
				my_bool = False
				subprocess.call('mv ' + top_dir + 'myTmp/testPic ' + top_dir + 'piecedPicture', shell=True)
				print('\nPicture file pieced together successfully.\n')
				print('The picture file can be found here: ' + top_dir + 'piecedPicture')
				print('The picture file order can be found here: ' + top_dir + 'fileOrder.txt\n')
				printFileOrder(local_list, top_dir + 'fileOrder.txt')
				break
			else:
				#User did not answer yes
				subprocess.call('rm -f ' + top_dir + 'myTmp/testPic',shell=True)

#Function: efficientPicFile
#Puprose: Run commands necessary to piece together a picture file except after adding every \
#	  piece, open the picture with eog (eye of gnome) and ask the user if it was the \
#	  correct piece. This function can be faster than inefficientPicFile assuming the \
#	  picture can display properly with only a couple of pieces added in at once. This \
#	  is known to work with GIF's and should work with other picture files
#Parameters: start_file = first file
#	     end_file = last file
#	     top_dir = directory containing the files to piece together
#Returns: True = if the file was pieced together successfully
#	  False = if the file was NOT pieced together successfully
def efficientPicFile(start_file, end_file, top_dir):
	files_list, list_length = createList(start_file, end_file, top_dir)
	the_ordered_list = []
	file_count = 0
	while_count = 0

	# if we know the first file, append it to our list of files in order
	if start_file:
		the_ordered_list.append(start_file)
		first_cmd = 'cat ' + top_dir + start_file + ' > ' + top_dir + 'myTmp/testPic'	
		subprocess.call(first_cmd, shell=True)

	while len(files_list) > 0 and while_count < list_length:
		current_file_count = file_count
		for aFile in (files_list):
			print('\nTrying to add ' + aFile)

			cmd = 'cat ' + top_dir + aFile + ' >> ' + top_dir + 'myTmp/testPic'
			subprocess.call(cmd, shell=True)
			subprocess.call('eog ' + top_dir + 'myTmp/testPic 2>/dev/null', shell=True)

			answer=string.strip(raw_input("Was this the next file? (y|n|q): "))

			if re.search('[qQ]|[qQ][uU][iI][tT]', answer):
				print('Quitting at request of user. Please delete temporary directories and any files created by this script in ' + top_dir + ' before attempting to run this script again.\n')
				sys.exit(2)
			elif re.search('[yY]|[yY][eE][sS]', answer):
				# This was the correct next file, add it to the list and \
				# increment the file_count
				the_ordered_list.append(aFile)
				file_count += 1
				break
			elif file_count == 0:
                                # User did not answer yes and this is first time \
				# through the loop.
				if first_file:
					# We know the first file so we just run first_cmd \
					# again so we can overwrite the test file with the \
					# appropriate first file.
					subprocess.call(first_cmd, shell=True)
				else:
					# We don't know the first file so we just remove \
					# the test file we created.
					subprocess.call('rm -f ' + top_dir + 'myTmp/testPic',shell=True)
			else:
                                # User did not answer yes and this is not first time \
				# through the loop, so we copy our saved good file to our \
				# test file.
				shutil.copy(top_dir + 'myTmp/thePicture', top_dir + 'myTmp/testPic')

		if current_file_count < file_count:
			shutil.copy(top_dir + 'myTmp/testPic', top_dir + 'myTmp/thePicture')
			for aFile in the_ordered_list:
				if aFile in files_list:
					files_list.remove(aFile)
			while_count += 1
		else:
			# We have looped through every file but couldn't figure out what the \
			# correct next file was.
			print('We were not able to piece together the file. Time to try another way.\n')
			return False

	if end_file:
		the_ordered_list.append(end_file)
                last_cmd = 'cat ' + top_dir + end_file + ' >> ' + top_dir + 'myTmp/testPic'
                subprocess.call(last_cmd, shell=True)

	subprocess.call('mv ' + top_dir + 'myTmp/testPic ' + top_dir + 'piecedPicture', shell=True)
	print('\nPicture file pieced together successfully.\n')
	print('The picture file can be found here: ' + top_dir + 'piecedPicture')
	print('The picture file order can be found here: ' + top_dir + 'fileOrder.txt\n')
	printFileOrder(the_ordered_list, top_dir + 'fileOrder.txt')

	return True

######################
#End Func.Definitions#
######################


######################
#        Main        #
######################
# zip file header: 504b 0304, but hexdump prints as different endian 4b50 0403
zip_file_reg_ex = '^4b50\s0403'

# jpg file header:   ffd8 (hexdump: d8ff)
# gif file header:   4749 4638 3761 (hexdump: 4947 3846 6137)
# gif file header 2: 4749 4638 3961 (hexdump: 4947 3846 6139)
# png file header:   504e 47 (hexdump: 4e50 ??47)
# png file header 2: ??50 4e47 (hexdump: 50?? 474e)
# bmp file header:   424d (hexdump: 4d42)
picture_file_reg_ex = '^d8ff|^4947\s3846\s6137$|^4947\s3846\s6139$|^4e50\s\w\w47|^50\w\w\s474e|^4d42'

if len(sys.argv) < 2:
	files_dir = os.getcwd()
	files_dir = files_dir + '/'
elif len(sys.argv) == 2:
	files_dir = sys.argv[1]
	if not re.match(".*/$", files_dir):
		files_dir = files_dir + '/'
else:
	#EDIT# should allow to specify beginning file and ending file on cli
	# perhaps allow to add other files too
	print('Error, too many command line arguments')
	sys.exit(1)


subprocess.call('mkdir -p ' + files_dir + 'myTmp/testing', shell=True)

# Try and determine the file type, first file and last file
file_type, first_file = determineFileType(files_dir)
last_file = determineLastFile(files_dir)

# Not sure what the file type is, so we definitely don't know the first file
if not file_type:
	file_type = askFileType()
	first_file = askFirstFile()

# Make sure we got the last file, if not ask
if not last_file:
	last_file = askLastFile()

if file_type == 'zip' or file_type == 1:
	zipFile(first_file, last_file, files_dir)
elif file_type == 'picture' or file_type == 2:
	ret_val = choosePicFileFunc(files_dir)
	if ret_val == 'inefficient':
		inefficientPicFile(first_file, last_file, files_dir)
	elif ret_val == 'efficient':
		if not efficientPicFile(first_file, last_file, files_dir):
			inefficientPicFile(first_file, last_file, files_dir)
	else:
		print('No clue what happened, but we did not get a proper return value value from the choosePicFileFunc function')
		sys.exit(1)
else:
	print "Need to put stuff here"

sys.exit(0)

######################
#      End Main      #	
######################
