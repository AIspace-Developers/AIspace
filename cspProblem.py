# cspProblem.py - Representations of a Constraint Satisfaction Problem
# Python 3 code. Full documentation at http://artint.info/code/python/code.pdf

# Artificial Intelligence: Foundations of Computational Agents
# http://artint.info
# Copyright David L Poole and Alan K Mackworth 2016.
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

from utilities import Displayable, dict_union

class Constraint(object):
    """A Constraint consists of
    * scope, a tuple of variables
    * a condition, a function that can applied to a tuple of values
    for the variables
    """
    def __init__(self, scope, condition):
        self.scope = scope
        self.condition = condition

    def __repr__(self):
        if len(self.scope) == 2:
            return ""+str(self.scope[0]) +" "+self.condition.__name__+" "+str(self.scope[1])
        else:
            returnStr = ""+self.condition.__name__ +" "
            for i in range(len(self.scope)):
                returnStr = returnStr + str(self.scope[i])
                if i != len(self.scope)-1:
                    returnStr = returnStr + ","
            return returnStr
        #return self.condition.__name__ + str(self.scope)

    def holds(self,assignment):
        """returns the value of Constraint con evaluated in assignment.

        precondition: all variables are assigned in assignment
        """
        return self.condition(*tuple(assignment[v] for v in self.scope))

class CSP(Displayable):
    """A CSP consists of
    * domains, a dictionary that maps each variable to its domain
    * constraints, a list of constraints
    """
    def __init__(self,domains,constraints,coordinates=None):
        self.variables = set(domains)
        self.domains = domains
        self.constraints = constraints
        self.coordinates = coordinates
        self.var_to_const = {var:set() for var in self.variables}
        for con in constraints:
            for var in con.scope:
                self.var_to_const[var].add(con)

    def __str__(self):
        """string representation of CSP"""
        return str(self.domains)

    def __repr__(self):
        """more detailed string representation of CSP"""
        return "CSP("+str(self.domains)+", "+str([str(c) for c in self.constraints])+")"

    def consistent(self,assignment):
        """returns True if all of the constraints that can be evaluated
        evaluate to True given the assignment.
        assignment is a variable:value dictionary
        """
        return all(con.holds(assignment)
                    for con in self.constraints
                    if all(v in  assignment  for v in con.scope))
                    
    def hasCoordinates(self):
        if self.coordinates is None:
            return False
        else:
            return True

