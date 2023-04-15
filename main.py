# This program aims to take in the text of python code from an input file and compile it into UC Davis CUSP version of assembly
# It is by no means meant to be comprehensive. It is more an experiment born out of curiosity than any attempt at productivity...

# My goals for the project are as follows:
# - be able to implement for loops, while loops, and conditional statements
# - properly allocate memory to both variables and instructions so that there are no memory leaks
# - be able to store and index through 1 dimensional arrays (yikes...)
# - maintain all variable names from the python program for clear, readable code

# Here's the high level version of my plan:
# Keep a program array with a bunch of "action" objects. Translate each line of code into its action.
# Each action object will be able to translate itself into assembly. They could be nested (for instance a for loop action
# could contain an arithmetic action) but the action.translate() method will get the string of assembly code
# Assign all those strings chronological locations in memory. Then once we have that figure out where to put the variables
# Finally, write the EQU's to initialize the variables in their proper places


# Possible types of actions:

# Comment:
# just kidding hahahahahaha. Commenting code? That's just a fairy tale they tell children. It doesn't exist

# Initialize variable
class InitializeVariable:

    def __init__(self, python):
        # the text from the input file
        self.python = python

        # the text of all the assembly code to complete this line of python code
        self.outputCode = ""
        # The number of lines of that output code (to make allocating memory easier)
        self.numLines = 3

        # the variable to be initialized
        self.variableToSet = self.python[:self.python.index(" = ")]

        self.actionType = "init"

        # for now only allowing ints lol
        self.varType = "int"

    def translate(self):
        self.outputCode = "\t.EQU " + self.variableToSet + ", MEMORY LOCATION\n\t.EQU @, MEMORY LOCATION\n\t.WORD 0"

    # we actually need a second translate function that adds in the memory #'s once we've calculated those
    def translateWithMemory(self, memoryLocation):
        self.outputCode = "\t.EQU " + self.variableToSet + ", "+str(memoryLocation)+"\n\t.EQU @, "+str(memoryLocation)+"\n\t.WORD 0"


# Set existing variable equal to something
# 1) Load the something into the accumulator
#   - "something" could be just a variable, a constant, an operation
#   - "a variable" can be a memory address or an index of an array
# 2) Store accumulator in the memory address of that variable

class SetVariable:

    def __init__(self, python):
        # the text from the input file
        self.python = python

        # the text of all the assembly code to complete this line of python code
        self.outputCode = ""
        # The number of lines of that output code (to make allocating memory easier)
        self.numLines = 0

        # the variable to be set
        self.variableToSet = self.python[:self.python.index(" = ")]

        # the "something" on the other side
        self.something = self.python[self.python.index(" = ") + 3:]

        self.actionType = "set"

    def translate(self):
        arithmetic = False
        for operation in "+-/*%":
            if operation in self.something:
                arithmetic = True
                setup = Operation(self.something, operation)
                setup.translate()
                setupText = setup.outputCode
                self.numLines += setup.numLines

        if not arithmetic:
            setupText = "\tLDA# " + self.something
            self.numLines += 1

        self.numLines += 1
        self.outputCode =  setupText + "\tSTA " + self.variableToSet


# Operations
# These include +, -, /, *, and %
# Takes in two quantities/variables and sets the accumulator equal to the result of that operation

class Operation:

    def __init__(self, python, symbol):
        # the text from the input file
        self.python = python

        # the operation to do
        self.symbol = symbol

        # the text of all the assembly code to complete this line of python code
        self.outputCode = ""
        # The number of lines of that output code (to make allocating memory easier)
        self.numLines = 2

        # the quantity on the left side
        self.leftSide = self.python[:self.python.index(" ")]

        # the quantity on the right side
        self.rightSide = self.python[self.python.index(" ") + 3:]

        self.actionType = "operation"

    def isVariable(self, thing):
        for letter in thing:
            if letter in "abcdefghijklmnopqrstuvwxyz":
                return True
        return False

    def translate(self):

        if self.isVariable(self.leftSide):
            self.outputCode += "\tLDA " + self.leftSide
        else:
            self.outputCode += "\tLDA# " + self.leftSide

        if self.symbol == "+":
            self.outputCode += "\n\tADA"

        elif self.symbol == "-":
            self.outputCode += "\n\tSBA"

        elif self.symbol == "*":
            self.outputCode += "\n\tMUL"

        elif self.symbol == "/":
            self.outputCode += "\n\tDIV"

        else:
            self.outputCode += "\tMOD"

        if self.isVariable(self.rightSide):
            self.outputCode += " " + self.rightSide + "\n"
        else:
            self.outputCode += "# " + self.rightSide + "\n"


# Now to start actually parsing the code we need a list of actions
actions = []

file = open("inputFile.txt", "r")
current = file.readline()

# first we need to do one full pass to initialize all the variables
initialized = []
while current != "":

    # if it's a line that sets a variable
    if " = " in current:
        leftSide = current[:current.index(" = ")]

        # if the variable is new
        if leftSide not in initialized:
            initialized.append(leftSide)
            actions.append(InitializeVariable(current))

    current = file.readline()

# now we reset for the second pass
file = open("inputFile.txt", "r")
current = file.readline()

while current != "":

    # we need to classify the type of action that current is
    # this means we're setting or initializing a variable
    if " = " in current:
        actions.append(SetVariable(current))

    current = file.readline()


# now we need to figure out where to store the variables
linesOfCode = 2
for action in actions:
    if action.actionType != "init":
        action.translate()
        linesOfCode += action.numLines

outputFile = open("outputFile.txt", "w")

firstLine = True
for action in actions:

    if action.actionType == "init":
        action.translateWithMemory(linesOfCode + 1)
        outputFile.write(action.outputCode + "\n")
        linesOfCode += 1

    else:
        if firstLine:
            firstLine = False
            outputFile.write("\t.EQU @, $000\n")

        outputFile.write(action.outputCode + "\n")

outputFile.write("\tHLT")
outputFile.close()