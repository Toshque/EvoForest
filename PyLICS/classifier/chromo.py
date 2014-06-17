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
        
        self.stateUseDict = {i:set() for i in set(list(self.boolStatements)+list(self.numStatements))}#<bool/num>statement:nodes of application
        self.originDict = {i:set() for i in self.numStatements}

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

    def getLocalAttrFitnessDict(self,node):
        '''calculates how important attributes are as a sum of (tree.numSamples) in all nodes divided by this attr'''
        d = {i:0. for i in set(list(self.numStatements)+list(self.boolStatements))}

        #enumerate all nodes
        allNodes = [self.tree]
        for i in allNodes:
            if not  i.isTerminal:
                allNodes+=[i.childPositive, i.childNegative]
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
        return self.fitness*len(self.samples)*(len(self.boolStatements)+len(self.numStatements))

    def expandBestStates(self,count):
        fdict = self.getLocalAttrFitnessDict()
        c=0
        while c < count:
            opID = random.randint(0,1)
            if opID == 0:
                state1,state2= helpers.proportionalrandom(self.numStatements,lambda x:fdict[x],2)
                newS = statements.get_sum([state1,state2])
                if self.addState(newS,numeric = True):
                    fdict[newS] = 0
                    c+=1

            elif opID ==1:
                state1,state2= helpers.proportionalrandom(self.numStatements,lambda x:fdict[x],2)
                newS = statements.get_mul(state1,state2)
                if self.addState(newS,numeric = True):
                    fdict[newS] = 0
                    c+=1
        #potential freezer
        return True
    def removeWorstStates(self,count):
        '''removes <count> least usefull attrs and returns true and removed attrs list. If this isn't possible, signals False and []'''    
        fdict = self.getLocalAttrFitnessDict()
        if count>= len(fdict):
            return False,[]
        else:
            deletionSequence = set(helpers.proportionalrandomNoRep(set(list(self.numStatements + self.boolStatements)),
                                                                  lambda x: fdict[x],count))
            
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
        self.stateUseDict[state] = set()
        return True
    def removeState(self,state,numeric=False):
        if not (state in self.numStatements or state in self.boolStatements):
            return False
        if numeric:
            self.numStatements.remove(state)
        else:
            self.boolStatements.remove(state)
        del self.stateUseDict[state]
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
        if origin != divisor: #not boolean statements
            self.stateUseDict[origin].add(node)
            self.originDict[divisor] = origin
        else:
            self.stateUseDict[divisor].add(node)
        
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
        self.fringe.remove(node.childPositive)
        self.fringe.remove(node.childNegative)
        self.fringe.add(node)

        self.numNodes-=1
        node.isTerminal = True
        del node.childPositive
        del node.childNegative
        node.dichotomy = None




