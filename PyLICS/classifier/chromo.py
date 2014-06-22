# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 19:45:34 2013

@author: sasha_000
"""

import helpers
import statements
import treeNode
import factor_connection
import copy
import random


cache = []

class attrNode:
    def __init__(self,attr):
        self.attr = attr
        self.parents = set()
        self.children = set()
    def isUsedAt(self, node):
        if node.isTerminal: return False
        return self.attr.toString() in node.dichotomy        
    def delete(self):
        self.parents = None
        self.children = None

import copy
class searchGraph:
    def __init__(self, states):
        self.attrs = {state: attrNode(state) for elem in self.numStatements}
    def expandState(self,state):
        pass #IMPLEMENT ME!
    def addState(self,state):
        if node not in attrs:
            self.attrs[state] = attrNode(attr)
    def removeState(self,state):
        for elem in self.attrs[state].parents:
            elem.children.remove(self)
        for elem in self.attrs[state].children:
            elem.parents.remove(self)
            
    def getUnion(self,other):
        newG = searchGraph([])
        newG.attrs = copy.deepcopy(self.attrs)
        for attr in other.attrs:
            if attr in self.attrs:
                newG.attrs[attr].parents = set(list(self.attrs[attr].parents)+list(other.attrs[attr].parents))
                newG.attrs[attr].children = set(list(self.attrs[attr].children)+list(other.attrs[attr].children))
            else:
                newG.attrs[attr] = copy.deepcopy(other.attrs[attr])
    
    def __del__(self):
        for node in self.attrs:
            node.delete()

class chromo:
    def __init__(self,system, samples, boolParams,numParams,fitness = 1.0):
        '''creates a unit decision maker for genetics'''

        self.samples = set(samples)
        self.keyStatements = set(system.keyStatements)
        self.numNodes = 0 #counting onle expanded trees
        self.tree = treeNode.treeNode(self.samples,self.keyStatements,system.isMajorant)
        self.fitness = fitness
        self.fringe = {self.tree}
        self.boolStatements = set(boolParams) #available boolean statements
        self.numStatements = set(numParams) #available numeric statements
        
        self.stateUseDict = {i:set() for     i in set(list(self.boolStatements)+list(self.numStatements))}#<bool/num>statement:nodes of application
        self.originDict = {}#dict X>C statement -> num statement X

    def classify(self,sample):
        return self.tree.classify(sample)
    def addSample(self,sample):
        if sample in self.samples:
            return False
        self.samples.add(sample)
        self.tree.addSample(sample)
        return True
    def removeSample(self,sample):
        self.samples.remove(sample)
        self.tree.removeSample(sample)
    def removeSamples(self,count):
        '''removes <count> least representative samples and returns true and removed samples list. If this isn't possible, signals False and []'''    
        if count>= len(self.samples):
            return False,[]
        else:
            deletionSequence = set(helpers.proportionalrandomNoRep(self.samples,lambda x: self.getLocalSampleFitness(x,self.tree),count))
            for sample in deletionSequence:
                self.removeSample(sample)
            return True, deletionSequence
    def getLocalSampleFitness(self,sample,node):
        '''calculates how important a sample is as a sum of 1/(numSamples) in all nodes where this sample is present'''
        s = 1./len(node.samples)
        if not node.isTerminal:
            cls = node.dichotomy.extractValue(sample)
            if cls: return s+ self.getLocalSampleFitness(sample,node.childPositive)
            else: return s+ self.getLocalSampleFitness(sample,node.childNegative)
        else:
            return s

    def getLocalAttrFitnessDict(self):
        '''calculates how important attributes are as a sum of (tree.numSamples) in all nodes divided by this attr'''
        d = {i:0. for i in list(self.numStatements)+list(self.boolStatements)}

        allNodes = helpers.getNodes(self.tree,False)
        n = {node: self.getDichotomyImportance(node) for node in allNodes}
        for state in d:
            for node in self.stateUseDict[state]:
                d[state] += n[node]
        return d
        
    def getReplacementPotential(self,node):
        return node.getEntropy()*len(node.samples)/(len(self.samples)) if len(self.samples)!=0 else 0 #if divisor's zero, last sample is removed as a penalty
    def getDichotomyImportance(self,node):
        '''works like information gain divided by a share of tree samples in the node'''
        if node.isTerminal:return 0
        return self.getReplacementPotential(node) - self.getReplacementPotential(node.childPositive) - self.getReplacementPotential(node.childNegative)


    def getBestReplacementPotential(self):
        return max(self.getReplacementPotential(node) for node in self.fringe)
    def getResourceWeight(self):
        '''heuristic estimate of CP time taken per loop in purple parrots'''
        return self.fitness*len(self.samples)*self.countStatements()
    def lenStatements(self):
        return len(self.boolStatements)+len(self.numStatements)
    def expandBestStates(self,count):
        '''does not necessarily increase by count,returns true count'''
        fdict = self.getLocalAttrFitnessDict()
        c=0
        for i in range(count):
            opID = random.randint(0,2)
            if opID == 0:
                if len(self.numStatements)<2:continue
                state1,state2= helpers.proportionalrandomNoRep(self.numStatements,lambda x:fdict[x],2)
                
                newS = statements.get_sum([state1,state2])
                if self.addState(newS,numeric = True):
                    fdict[newS] = 0
                    c+=1
            elif opID ==1:
                if len(self.numStatements)<2:continue
                state1,state2= helpers.proportionalrandomNoRep(self.numStatements,lambda x:fdict[x],2)
                newS = statements.get_sum([state1,statements.get_minus(state2)])
                if self.addState(newS,numeric = True):
                    fdict[newS] = 0
                    c+=1
            elif opID ==2:
                if len(self.numStatements)<2:continue
                state1,state2= helpers.proportionalrandomNoRep(self.numStatements,lambda x:fdict[x],2)#cannot be used as power
                newS = statements.get_mul([state1,state2])
                if self.addState(newS,numeric = True):
                    fdict[newS] = 0
                    c+=1
        return c
    def removeWorstStates(self,count):
        '''removes <count> least usefull attrs and returns true and removed attrs list. If this isn't possible, signals False and []'''    
        fdict = self.getLocalAttrFitnessDict()
        if count>= len(fdict):
            return False,[]
        else:
            zeroes = filter(lambda x:fdict[x]==0,fdict.keys())
            
            deletionSequence = []
            if len(zeroes) >=count:
                deletionSequence+= random.sample(zeroes,count)
            else:
                deletionSequence += zeroes
                nonzeroes = filter(lambda x:fdict[x]!=0,fdict.keys())
            
                deletionSequence += list(helpers.proportionalrandomNoRep(nonzeroes,
                                                                  lambda x: fdict[x],count-len(zeroes)))
            
            for attr in deletionSequence:
                self.removeState(attr)
            return True, deletionSequence


    def addState(self,state,numeric=False):
        if state in self.numStatements or state in self.boolStatements:
            return False
        if numeric:
            self.numStatements.add(state)
        else:
            self.boolStatements.add(state)
        if state not in self.stateUseDict:#could have been left there since the previous equal statement, that is now removed.
            self.stateUseDict[state] = set()
        
        return True
    def removeState(self,state):
        if not (state in self.numStatements or state in self.boolStatements):
            return False
        numeric = state in self.numStatements
        if numeric:
            self.numStatements.remove(state)
        else:
            self.boolStatements.remove(state)
        
        return True
        
    def expandBestNode(self):
        nmax, pmax = None, None
        for node in self.fringe:
            if self.getReplacementPotential(node) > pmax:
                pmax = self.getReplacementPotential(node)
                nmax = node
        if self.extend(nmax):
            return True
        return False
    def extend(self,node):
        divisor,origin = factor_connection.getBestLink(node.keyStatements,node.samples,self.boolStatements,self.numStatements,True)
        if divisor == False:
            return False;

        self.stateUseDict[origin].add(node)
        if origin != divisor: #not boolean statements    
            self.originDict[divisor] = origin
        
        node.expand(divisor)
        self.fringe.add(node.childPositive)
        self.fringe.add(node.childNegative)
        self.fringe.remove(node)
        self.numNodes +=1
        return True
    def pruneWorstNode(self):
        if self.numNodes ==1:
            return False
        olist = [self.tree]
        minIG = float('inf')
        minIGNode = None
        while olist !=[]:
            cur = olist.pop()
            if not cur.isTerminal: 
                olist.append(cur.childPositive)
                olist.append(cur.childNegative)
                if cur.childPositive.isTerminal and cur.childNegative.isTerminal:#if it is above leafs
                    if self.getReplacementPotential(cur) < minIG:
                        minIG = self.getReplacementPotential(cur)
                        minIGNode = cur
        self.prune(minIGNode)
        return True
    def prune(self,node):
        if node.childPositive not in self.fringe or node.childNegative not in self.fringe:
            return False

        state = node.dichotomy
        if node.dichotomy in self.originDict:
            state = self.originDict[node.dichotomy]
            del self.originDict[node.dichotomy]

        
        self.stateUseDict[state].remove(node)
        
        if len(self.stateUseDict[state]) == 0:
            if state not in self.numStatements and state not in self.boolStatements:
                 del self.stateUseDict[state]
        
        self.fringe.remove(node.childPositive)
        self.fringe.remove(node.childNegative)
        self.fringe.add(node)

        self.numNodes-=1
        node.isTerminal = True
        del node.childPositive
        del node.childNegative
        node.dichotomy = None




