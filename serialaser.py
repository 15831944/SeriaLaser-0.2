# serialaser.py -- send/recv data over COM1

import serial
import time
import re
from sys import argv
from optparse import OptionParser

# Windows newline
MSNewline = serial.CR+serial.LF

# /.n[iu]x/ newline
realNewline = serial.LF


# Initialize serial port
ser = serial.Serial()
ser.port     = 0
ser.baudrate = 9600
ser.bytesize = serial.SEVENBITS
ser.parity   = serial.PARITY_EVEN
ser.rtscts   = True
ser.xonxoff  = True
ser.timeout  = 1

def send_progs(program, ePack, quiet):
	ser.open()
	ser.write('\x12%') # Device control 2 (\x12), not sure it's necessary.
	
	# According to a guy on 
	# <http://www.cnczone.com/forums/fanuc/34946-serial_port_issues_ge_fanuc_ot-c.html>,
	# 'The Fanuc requires a Line-Feed character, or LF before 
	# the first block of the program. This cancels the LSK, or 
	# "Label Skip" function on the control.'
	ser.write(serial.LF)
	
	for i in program:
		# Whitespace destroyer
                line = re.sub("\ ", "", i)
                if ePack:
                        line = re.sub("^E[1-9]0?$", ("E" + str(ePack)), line)
                if not quiet:
                        print line
		ser.write(line)
	# done with port
	ser.write('%')
	ser.close()
        # That was easy!

def recv_progs():
	regexString = ":.*\(?"
	
	ser.open()
	program = str("")
	length = 0
	while True:
		x = str(ser.read())
		program = program + x
		if len(program) > 0:
			if program[len(program) - 1] == '\x14': # It seems to send device control 4 '\x14' when it's done.
				break
	# Done with COM1
	ser.close()

	regexFilename = re.search(regexString, program)
	if regexFilename.group(0) != None:
		aFilename = regexFilename.group(0)[1:-1]
	else:
		# I'm doing this to create a unique fileName in the event of not
		# finding one in the incoming data. 
		aFilename = str(time.gmtime().tm_yday) + str(time.gmtime().tm_hour) + str(time.gmtime().tm_min) + str(time.gmtime().tm_sec)
	finalFilename = "O"+str(aFilename)+".LCD"

	newProgram = open(finalFilename, "w")
	for i in program:
		newProgram.write(str(i))
	print "Wrote \"" + finalFilename + "\""

        # Of course, this function is never used.

def mainprog(argv):
        usage = "usage: %prog [options]"
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="fileName", action="store", 
                          help="file to send to laser")
        parser.add_option("-e", "--e-pack", dest="ePack", action="store", 
                          help="set all cut conditions to a single condition")
        parser.add_option("-q", "--quiet", action="store_false", 
                          dest="verbose", default=True, 
                          help="don't print program lines to stdout.")
        (options, args) = parser.parse_args()
        program = open(options.fileName)
        send_progs(program, options.ePack, options.verbose)
        program.close()

if __name__ == "__main__":
        if len(argv) > 1:
                mainprog(argv)
	else:
		recv_progs()

