fileStitch
==========
###############
## Author(s) ##
###############
Stephan Gross (a.k.a. persebek), original creator/author  
Contact: stephan@sgrosshome.com

############
## Github ##
############
url: https://github.com/persebek/fileStitch  
ssh: git@github.com:persebek/fileStitch.git  
svn: https://github.com/persebek/fileStitch

###############
## Licensing ##
###############
This software is distributed under the GPLv3 license, which should be included in the file called, LICENSE, located in this same directory.  If the LICENSE file is not included, the GPLv3 license can be viewed here http://www.gnu.org/licenses/gpl.html.

##########
## Uses ##
##########
This program can be used to piece or "stitch" together a file that was broken up into separate parts.  Currently it works with zip files, and different picture files such as jpg, bmp, and png.

##########
## Why? ##
##########
I created this program to help solve a challenge found in some cyber competitions, which is often called a "file carve challenge".  In these challenges you would be given a file that was split into multiple pieces (other, smaller files), and your task was to concatenate the pieces in the correct order to create the original file.  The original file that was split could be anything, a zip file, a picture file, an mp3, etc...The names of the pieces were usually arbitrary, such as a sequence of four numbers (ex: 6345, 1423, 8734, and 9856), leaving you without any clue as to the order of the pieces.  Usually you had to manually run the cat (on Linux) or type (on Windows) command on the files to find the answer (ex: cat 1423 8734 9856 6345 > original-file).  If the first file sequence you tried didn't work, then you would keep trying sequences until you found the correct order and successfully created the original file.

This process could be very time consuming, especially if the file was split into many different pieces (usually there were 6 or more). So, in an attempt to solve the challenge more efficiently, this program was born.  At first I created this program and made it available to others on the University of Maryland University College Cyber Padawans team, under the name of "pieceFileCarve.py".  I decided to make this program available to the public in order to provide others with this option for a competition, possibly receive improvements to the program from others, and to hopefully inspire others to create a similar and perhaps better version.  When releasing this to the public I decided to change the name to fileStitch.py, since it is more descriptive of what the program does.

##################
## Requirements ##
##################
-   GUI system  
    Only necessary if wanting to stitch together a picture file

-   Python  
    To current knowledge, this program should work with any version of Python 2.5 or higher.  Please send an email      if you find this program to not work with a specific version of Python.

-   eog (eye of gnome)  
    This is required to verify picture files were correctly pieced together. In future versions, I hope to have      fileStitch be able to automatically search for eog, a KDE equivalent, or ask the user to specify a path to a      binary of a similar program.
