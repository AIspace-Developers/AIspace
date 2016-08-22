# utilities.py - AIFCA utilities
# Python 3 code. Full documentation at http://artint.info/code/python/code.pdf

# Artificial Intelligence: Foundations of Computational Agents
# http://artint.info
# Copyright David L Poole and Alan K Mackworth 2016.
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

# This code is specialized to work in a Jupyter Notebook environment
# For CSP, notebookCSPSetup is required. For other algorithms, it should not affect execution

from notebookCSPSetup import reduceDomain, highlightArc, restoreDomains
from time import sleep
from threading import Thread
import IPython.display as dsply
from ipywidgets import widgets

global blockAlg
global newStepLvl
newStepLvl = 0
global manualStepToggle #0 is inert, 1 switches to false, 2 switches to true
manualStepToggle = 0


class Displayable(object):
    max_display_level = 1   # can be overridden in subclasses
    max_step_level = 1     # can be overridden in subclasses
    manual_step = False     # can be overridden in subclasses
    # if manual_step == true, require user input to complete execution
    auto_step_speed = 1     # can be overridden in subclasses

    def display(self,level,*args,**kwargs):
        """print the arguments if level is less than or equal to the
        current max_display_level.
        level is an integer.
        the other arguments are whatever arguments print can take.
        """
        #Print args based on level
        if level <= self.max_display_level:
            print(*args)  ##if error you are using Python2 not Python3
            
		#Debugging full-printout	
        if level == -1:
            print("These are the args", *args)
            print("These are the **kwargs", kwargs)
                
        #For CSP domain pruning, args[2] = id of node, kwargs = elements to prune
        #This code block will trigger the visualization to prune the domain of a variable
        if args[0] == 'Domain pruned':
            nodeName = args[2]
            consName = args[6]
            for key, value in kwargs.items():
                elementValues = value
                for elementValue in elementValues:
                    reduceDomain(nodeName, elementValue)
            
        #For CSP arc highlighting, args[1] = id of Var, args[3] = Constraint
        #This code block will trigger the visualization to highlight a specific arc
        #Blue: Needs to be considered
        #Green: Consistent
        #Red: Inconsistent
        #Bold: Currently considering
        if args[0] == "Processing arc (":
            varName = args[1]
            consName = args[3]
            #print(args)
            #print(varName, consName.__repr__())
            highlightArc(varName, consName.__repr__(), "bold","na")
            
        if args[0] == 'Domain pruned':
            varName = args[2]
            consName = args[6]
            highlightArc(varName, consName.__repr__(), "bold","green")
            
        if args[0] == "Arc: (" and args[4] == ") is inconsistent":
            varName = args[1]
            consName = args[3]
            highlightArc(varName, consName.__repr__(), "bold","red")
            
        if args[0] == "Arc: (" and args[4] == ") now consistent":
            varName = args[1]
            consName = args[3]
            highlightArc(varName, consName.__repr__(), "!bold","green")
            
        #For CSP arc consistency, args[1] = list of arcs to add
        #This code clock will trigger the vizualization to add an arc back to the to_do list
        #Added arcs will be blue
        if args[0] == "  adding" and args[2] == "to to_do.":
            if args[1] != "nothing":
                arcList = list(args[1])
                for i in range(len(arcList)):
                    highlightArc(arcList[i][0], arcList[i][1].__repr__(), "!bold", "blue")

        #Control whether the algorithm proceeds on its own or requires user input
        global manualStepToggle
        if (manualStepToggle == 1):
            self.manual_step = False
            manualStepToggle = 0
        elif (manualStepToggle == 2):
            self.manual_step = True
            manualStepToggle = 0
            
        #Pause execution based on level
        if level <= self.max_step_level:
            if self.manual_step:
                global blockAlg, newStepLvl
                blockAlg = 1
                spin() #spin and wait for a stepButton press
                if (newStepLvl != 0):
                    self.max_step_level = newStepLvl
                    self.max_display_level = newStepLvl
                    newStepLvl = 0
                print("current step_level:", self.max_step_level)
            else:
                #print("Automated pause level", self.max_step_level)
                sleep(self.auto_step_speed)
                
        #if args[0] == "AC done. Reduced domains":
        #    showResetButton()
        
        #If AC starts, set all domains back to initial values and make all arcs blue
        if args[0] == "AC starting":
            restoreDomains()
            highlightArc("all", "all", "!bold", "blue")

import random

def argmax(gen):
    """gen is a generator of (element,value) pairs, where value is a real.
    argmax returns an element with maximal value.
    If there are multiple elements with the max value, one is returned at random.
    """
    maxv = float('-Infinity')       # negative infinity
    maxvals = []      # list of maximal elements
    for (e,v) in gen:
        if v>maxv:
            maxvals,maxv = [e], v
        elif v==maxv:
            maxvals.append(e)
    return random.choice(maxvals)

def flip(prob):
    """return true with probability prob"""
    return random.random() < prob

def dict_union(d1,d2):
    """returns a dictionary that contains the keys of d1 and d2.
    The value for each key that is in d2 is the value from d2,
    otherwise it is the value from d1.
    This does not have side effects.
    """
    d = dict(d1)    # copy d1
    d.update(d2)
    return d
    
import json
def cspToJson(cspObject):
    """cspToJson takes a cspObject and creates a JSON representation.
    This representation has the form:
    {'nodes': [], 'constrains': [], 'coordinates: []}
    """
    if cspObject.hasCoordinates():
        pythonRep = {'nodes': [],
                 'constraints': [],
                 'coordinates': cspObject.coordinates}
    else:
        pythonRep = {'nodes': [],
                 'constraints': []}
    for var in cspObject.domains:
        temp = {'name': var, 'domain': ','.join(str(s) for s in cspObject.domains[var])}
        pythonRep['nodes'].append(temp)
    for cons in cspObject.constraints:
        tempArr = []
        for i in range(len(cons.scope)):
            tempArr.append(cons.scope[i])
        temp = {'nodes': tempArr, 'constraint': cons.condition.__name__, 'string': cons.__repr__()}
        pythonRep['constraints'].append(temp)

    jsonRep = json.dumps(pythonRep)
    return jsonRep

class threadWR(Thread):
    """threadWR is a thread extended to allow a return value.
    To get the return value, use this thread as normal, but assign it to a variable on creation.
    calling var.join() will return the return value.
    the return value can also be gotten directly via ._return, but this is not safe.
    """
    def __init__(self, *args, **kwargs):
        super(threadWR, self).__init__(*args, **kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super(threadWR, self).join(*args, **kwargs)
        return self._return
        
def setupGUI(func=None,*args,**kwargs):
    """setupGUI creates the GUI required to control the executing visualization"""
    def click_step1(b):
        #print("lvl1 Button clicked")
        global newStepLvl
        newStepLvl = 1
        dsply.clear_output(wait=True)
        global blockAlg
        blockAlg = 0

    def click_step2(b):
        #print("lvl2 Button clicked")
        global newStepLvl
        newStepLvl = 2
        dsply.clear_output(wait=True)
        global blockAlg
        blockAlg = 0

    def click_step3(b):
        #print("lvl3 Button clicked")
        global newStepLvl
        newStepLvl = 3
        dsply.clear_output(wait=True)
        global blockAlg
        blockAlg = 0
        
    def click_step4(b):
        #print("lvl4 Button clicked")
        global newStepLvl
        newStepLvl = 4
        dsply.clear_output(wait=True)
        global blockAlg
        blockAlg = 0

    lvl1Button = widgets.Button(description="AutoSolve Fast")
    lvl2Button = widgets.Button(description="Step")
    lvl3Button = widgets.Button(description="Step fine")
    lvl4Button = widgets.Button(description="Fine Step")
    
    lvl1Button.on_click(click_step1)
    #lvl1Button.layout.width = '100px'
    lvl2Button.on_click(click_step2)
    #lvl2Button.layout.width = '100px'
    lvl3Button.on_click(click_step3)
    #lvl3Button.layout.width = '100px'
    lvl4Button.on_click(click_step4)
    #lvl4Button.layout.width = '100px'
    
    def click_play(b):
        #print("play button")
        global manualStepToggle, blockAlg
        dsply.clear_output(wait=True)
        manualStepToggle = 1
        blockAlg = 0
        
    def click_pause(b):
        #print("pause button")
        global manualStepToggle
        manualStepToggle = 2
        #dsply.clear_output(wait=True)
    
    autoButton = widgets.Button(description="AutoSolve")
    autoButton.on_click(click_play)
    pauseButton = widgets.Button(description="Stop")
    pauseButton.on_click(click_pause)
    
    #autoButton.layout.width = '70px'
    #pauseButton.layout.width = '70px'
    
    def click_reset(b):
        restoreDomains()
        highlightArc("all", "all", "!bold", "blue")
        executeThread(func, args, kwargs)
        dsply.clear_output(wait=True)
    
    resetButton = widgets.Button(description="Reset")
    resetButton.on_click(click_reset)
    
    buttonGroup = [lvl4Button, lvl2Button, autoButton, pauseButton, lvl1Button, resetButton]
    buttonContainer = widgets.HBox(children=buttonGroup)
    dsply.display(buttonContainer)

#spin blocks until blockAlg == 0. Functionally, this blocks until user supplies input
def spin():
    while blockAlg == 1:
        #print("spinning")
        sleep(0.1)
        
# startAlgorithm uses the 1st method of creating a thread (documented below) and also
# creates the GUI for controlling the execution of the thread.        
def startAlgorithm(func, *args, **kwargs):
    setupGUI(func, args, kwargs)
    return executeThread(func, args, kwargs)
    
# 2 ways of creating threads for computations: executeThrd and callRecurse
# 1, executeThrd: Wrap your work in a function, including a return value if any
#   call executeThrd(function). If a return value is needed, assign the return
#   of the call to a variable, and take ._return. _return is not thread safe
    
def executeThread(func, *args, **kwargs):
    eThread = threadWR(target=func, args=args, kwargs=kwargs)
    eThread.start()
    return eThread

# 2, callRecurse: For a chain of function calls, where each uses the output of
#   the previous as input, use callRecurse(func1, func2, func3, ..., args). Note
#   args will only be applied to the innermost function. Return is handled the
#   same way as executeThread
#   This is not the preferred method
def callRecurse(func, *args):
    #print(args)
    #print(*args)
    #print(args[0])
    thrd = threadWR(target=recursiveThrd, args=(func,*args))
    thrd.start()
    return thrd
    
# recursiveThrd is used by callRecurse
def recursiveThrd(func, *args):
    if callable(args[0]):
        listArgs = list(args)
        del listArgs[0]
        collapseReturn = recursiveThrd(args[0], *listArgs)
        interReturn = func.__call__(collapseReturn)
        
    else:
        interReturn = func.__call__(*args)
    return interReturn
