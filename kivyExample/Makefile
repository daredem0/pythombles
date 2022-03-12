#Signifies our desired python version
WINDOWS_T = "windows"
LINUX_T = "linux"
 
ifeq ($(OS),Windows_NT)
	PYTHON = python
	SEP=;
	SYS=WINDOWS_T
else
	PYTHON = python3#
	SEP=:
	SYS=LINUX_T
endif
# Specify config path
WSL= wsl -d Ubuntu-18.04 sh -c

TARGET = ./kivyExample
DATA_FILES = "./ui${SEP}./ui"
# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = help

# Defines the default target that `make` will to try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = help

ifeq ( ${SYS}, ${WINDOWS_T})
	pyinstaller_binary = pyinstaller --onefile --add-data ${DATA_FILES} ${TARGET}.spec
else
	pyinstaller_binary = pyinstaller --onefile --add-data ${DATA_FILES} ${TARGET}.py
endif

help:
	@echo "------------------------------HELP---------------------------"
	@echo "To check the current target system type make status"
	@echo "To build the the project executable type make binary"
	@echo "To clean up type make clean"
	@echo "To also clean up generated binaries type make distclean"
	@echo "-------------------------------------------------------------"


# The ${} notation is specific to the make syntax and is very similar to bash's $()

binary:
	[ ${SYS} != ${WINDOWS_T} ] && cp ${TARGET}.spec ${TARGET}.spec.sav
	${pyinstaller_binary}
	[ ${SYS} != ${WINDOWS_T} ] && mv ${TARGET}.spec.sav ${TARGET}.spec

clean:
	rm -rf ./build
	
distclean:
	rm -rf ./dist


