# cspConsistency.py - Arc Consistency and Domain splitting for solving a CSP
# Python 3 code. Full documentation at http://artint.info/code/python/code.pdf

# Artificial Intelligence: Foundations of Computational Agents
# http://artint.info
# Copyright David L Poole and Alan K Mackworth 2016.
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

# This code is specialized to work in a Jupter Notebook environment, but it should still work otherwise

from utilities import Displayable

class Con_solver(Displayable):
    def __init__(self, csp, domains=None):
        self.csp=csp
        if domains is not None:
            self.domains = domains
        else:
            self.domains = csp.domains.copy()

    def __repr__(self):
        return str(self.domains)
        
    def make_arc_consistent(self,to_do=None):
        """Makes this CSP arc-consistent using generalized arc consistency
        to_do is a set of (variable,constraint) pairs
        """
        if to_do is None:
            to_do = {(var,const) for const in self.csp.constraints
                             for var in const.scope}
        else:
            to_do = to_do.copy()  # use a copy of to_do
        self.display(4,"AC starting",self.domains)
        while to_do:
            #Select arc, determine if it is consistent, prune, add arcs to to-do list, mark arc as consistent
            var,const = to_do.pop()
            self.display(2,"Processing arc (",var,",",const,")")
            other_vars = [ov for ov in const.scope if ov is not var]
            new_domain = {val for val in self.domains[var]
                          if self.any_holds(const,{var:val},other_vars,0)}
            removed_vars = self.domains[var] - new_domain
            if new_domain != self.domains[var]:
                self.display(4,"Arc: (",var,",",const,") is inconsistent")
                self.display(3,"Domain pruned","dom(",var,") =",new_domain," due to ",const, varName=removed_vars)
                self.domains[var] = new_domain
                add_to_do = self.new_to_do(var,const)
                to_do |= add_to_do      # set union
                self.display(3,"  adding",add_to_do if add_to_do else "nothing", "to to_do.")
            self.display(4,"Arc: (",var,",",const,") now consistent")
        self.display(2,"AC done. Reduced domains",self.domains)

    def new_to_do(self,var,const):
         """returns new elements to be added to to_do after assigning
         variable var in constraint const.
         """
         return {(nvar,nconst) for nconst in self.csp.var_to_const[var]
                               if nconst != const
                               for nvar in nconst.scope
                               if nvar != var}

    def any_holds(self,const,env,other_vars,ind):
        """returns True if Constraint const holds for an assignment
        that extends env with the variables in other_vars[ind:]
        env is a dictionary
        Warning: this has side effects and changes the elements of env
        """
        if ind==len(other_vars):
            return const.holds(env)
        else:
            var = other_vars[ind]
            for val in self.domains[var]:
                #env = dict_union(env,{var:val})  # no side effects!
                env[var] = val
                if self.any_holds(const,env,other_vars,ind+1):
                    return True
            return False

    def copy_with_assign(self, var=None, new_domain={True,False}):
        """create a copy of the CSP with an assignment var=new_domain
        if var==None then it is just a copy.
        """
        newdoms = self.domains.copy()
        if var:
            newdoms[var] = new_domain
        return Con_solver(self.csp,newdoms)


    def solve_one(self,to_do=None):
        """return a solution to the current CSP or False if there are no solutions
        to_do is the list of arcs to check
        """
        self.make_arc_consistent(to_do)
        if any(len(self.domains[var])==0 for var in self.domains):
            return False
        elif all(len(self.domains[var])==1 for var in self.domains):
            self.display(2,"solution:", {var:select(self.domains[var])  for var in self.domains})
            return {var:select(self.domains[var])  for var in self.domains}
        else:
            var = select(x for x in self.csp.variables if len(self.domains[x])>1)
            if var:
                split = len(self.domains[var])//2
                dom1 = set(list(self.domains[var])[:split]) #a nonempty proper subset
                csp1 = self.copy_with_assign(var,dom1) # copy with dom(var)=dom1
                dom2 = self.domains[var]-dom1
                csp2 = self.copy_with_assign(var,dom2) # copy with dom(var)=dom2
                self.display(3,"...splitting",var,"into",dom1,"and",dom2)
                to_do = self.new_to_do(var,None)
                return csp1.solve_one(to_do) or csp2.solve_one(to_do) 

from searchProblem import Search_problem

class Search_with_AC_from_CSP(Search_problem,Displayable):
    """A search problem with arc consistency and domain splitting

    A node is a CSP """
    def __init__(self, csp):
        self.cons = Con_solver(csp)  #copy of the CSP
        self.cons.make_arc_consistent() # this has side effects

    def is_goal(self, node):
        """node is a goal if all domains have 1 element"""
        return all(len(node.domains[var])==1 for var in node.domains)
    
    def start_nodes(self):
        return [self.cons]
    
    def neighbor_nodes(self,node):
        """an iterator over the neighboring nodes of node.
        This is used for depth-first search"""
        var = select(x for x in node.domains if len(node.domains[x])>1)
        if var:
            split = len(node.domains[var])//2
            dom1 = set(list(node.domains[var])[:split]) #a nonempty proper subset
            dom2 = node.domains[var]-dom1
            self.display(2,"Splitting", var, "into", dom1, "and", dom2)
            to_do = node.new_to_do(var,None)
            for dom in [dom1,dom2]:
                newcsp = node.copy_with_assign(var,dom)
                newcsp.make_arc_consistent(to_do)
                if all(len(newcsp.domains[v])>0 for v in newcsp.domains):
                    # all domains are non-empty
                    yield newcsp
                else:
                    self.display(2,"...",var,"in",dom,"has no solution")

def select(iterable):
    """select an element of iterable. Returns None if there is no such element.
    
    This implementation just picks the first element.
    For many of the uses, which element is selected does not affect correctness, 
    but may affect efficiency.
    """
    for e in iterable:
        return e    #returns first element found

from cspExamples import csp1, csp2, crossword1, crossword2, crossword2d
from searchDepthFirst import Depth_first_search

## Test Solving CSPs with Arc consistency and domain splitting:
#Con_solver(csp1).solve_one()
#searcher1d = Depth_first_search(Search_with_AC_from_CSP(csp1))
#print(searcher1d.search().domains)
#Depth_first_search.max_display_level = 2  # display search trace (0 turns off)
#searcher2c = Depth_first_search(Search_with_AC_from_CSP(csp2))
#print(searcher2c.search().domains)
#searcher3c = Depth_first_search(Search_with_AC_from_CSP(crossword1))
#print(searcher3c.search() .domains)
#searcher4c = Depth_first_search(Search_with_AC_from_CSP(crossword2))
#print(searcher4c.search().domains)
#searcher5c = Depth_first_search(Search_with_AC_from_CSP(crossword2d))
#print(searcher5c.search().domains)

