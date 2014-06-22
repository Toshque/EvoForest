# -*- coding: utf-8 -*-
#some useful, but not major functions
import random


def isCorrectForSample(tree, sample):
    '''check if tree.classify(sample) matches keystates themselves. The sample must have them defined,ofc. tree is anything that has 'classify(sample)->dict(keystate:value)' method'''
    rdict = tree.classify(sample)
    for state in rdict:
        if rdict[state] != state.extractValue(sample):
            return False
    return True
def getSuccessProbability(tree,samples):
    return sum(int(isCorrectForSample(tree,sample)) for sample in samples)/float(len(samples))
        


def sortedRandomSequence(count,max):
    total = max
    if (count >50):# this generator is both valid only for big count and O(count) in time&memory. The number 50 was whispered by one squirel
        v = 0 
        for i in range(count):
            if (v != total):
                v += min(random.expovariate((count-i)/float(total-v)),total-v)
            yield v
    else:
        r = [random.Random().uniform(0,total) for ei in range(count)]
        r.sort(reverse = True)
        while r != []:
            yield r.pop()

def proportionalrandom(items,fpriority,count = 1):
    """choose a sample of [count] elements from [items] list with probability of ith elem taken equals [fpriority(i)/sum(fpriority)]. note that no probability must be below 0; output sequence is containing elements in the same order as the original one."""
    items = list(items)
    sums =[0]# in order for item i to be chosen, r value must be between sums[i] and sums[i+1], works for i-s
    for i in items:
        sums.append(sums[-1]+fpriority(i))
    total = sums[-1]
    r = sortedRandomSequence(count,total)
    samples = []
    si = 0#sample index
    for ri in r:
        while ri> sums[si+1]:
            si+=1
        samples.append(items[si])
            
    return samples
import copy
def proportionalrandomNoRep(items, fpriority, count):
    """same as proportional random but does not include repetitions and returns a seq of a guaranteed length. NO LONGER SORTED!"""
    assert(len(items)>=count)

    items = copy.copy(items)

    r = set()
    while(len(r) != count):
        for el in set(proportionalrandom(items,fpriority,count-len(r))):
            items.remove(el)
            r.add(el)
    return list(r)

import time
class logWriter:
    def __init__(self):
        '''logWriter is an aux class that is playing a virtual log file role with pointers'''
        self.string = ''
        self.pointer = 0 #used to read by blocks
        self.timeMarkers = {'general' :time.clock()}
        
    def printToConsole(self):
        if self.pointer >= len( self.string):
            print "<No new log>"
        print self.string[self.pointer:]
        self.pointer = len( self.string)
    def readString(self):
        if self.pointer >= len( self.string):
            return ""
        s= self.string[self.pointer:]
        self.pointer = len( self.string)
        return s
    def timeMarker(self,markerName = 'general',sinceLast = True,reset = True):
        '''print current time, save it with a name specified, write timespan since last call if flag is true(default)
        if reset flag is active(default), resets the marker to now'''
        if sinceLast: 
            self.string += str(time.clock() - self.timeMarkers[markerName]) + ' seconds spent for '+markerName+' \n'
        self.timeMarkers[markerName] = time.clock()
    def currentTime(self):
        self.string += time.ctime() + '\n'

    def writeLine(self,*args):
        for arg in args:
            self.string += str(arg) + ' '
        self.string += '\n'
    def removeOld(self):
        self.string = self.string[self.pointer:]
        self.pointer = 0

def mul(sequence):
    '''product of sequence elements'''
    m=1
    for elem in sequence:
        m*=elem
    return m
def getNodes(tree,includeLeafs = True):
    '''all the nodes in the tree as list'''
    allNodes = [tree]
    for node in allNodes:
        if not node.isTerminal:
            if includeLeafs or (not node.childPositive.isTerminal):
                allNodes.append(node.childPositive)
            if includeLeafs or (not node.childNegative.isTerminal):
                allNodes.append(node.childNegative)
    return allNodes
def getSize(classification,includeLeafs = True):
    '''returns the amount of nodes in the current the tree classification'''
    olist = [classification]
    size = 0
    while olist !=[]:
        cur = olist.pop()
        if (not cur.isTerminal) or (includeLeafs):size +=1
        if not cur.isTerminal: 
            olist.append(cur.childPositive)
            olist.append(cur.childNegative)
    return size
def getMajorant(states, samples, smoothing = 0):
    #majorant vector used to generate result vector for keyStatements
    states = list(states)
    if len(samples) ==0:
        raise ValueError,"explain me why would you do that?(count majorant of an empty set)"
    options = [tuple(statement.extractValue(sample) for statement in states) for sample in samples]
    maxOpt = None
    maxVal = -float('inf')
    for option in set(options):
        val = options.count(option)
        if val>maxVal:
            maxVal = val
            maxOpt = option
    assert maxOpt != None
    return {states[i]:maxOpt[i] for i in range(len(maxOpt))}
        



def getAverage(states, samples, smoothing = 0):
    #list of averages used to generate result vector for keyStatements
    return {statement:getProbability(statement,samples,smoothing) for statement in states}
def getProbability (state, samples,smoothing = 0):
    cnt = 0. + smoothing
    for sample in samples:
        if state.extractValue(sample):
            cnt +=sample._weight
    if cnt ==0: return 0.
    return cnt/(sum(i._weight for i in samples) + 2*smoothing)

def getBoolEntropy(samples,keyStatements, b=2):
    import math
    keyStatements = list(keyStatements)
    ent = 0.
    outcomes = [0. for i in range(2**len(keyStatements))]
    norm = sum(i._weight for i in samples)+0.
    for sample in samples:
        outcomeID = 0
        for i in range(len(keyStatements)):
            if keyStatements[i].extractValue(sample):
                outcomeID += 2**i
        outcomes[outcomeID] += sample._weight
    
    for outcome in outcomes:
        if outcome ==0:continue
        p = outcome/norm
        if p ==0 or norm ==0 : continue #lim(p->0)p * log p  = 0
        ent -= p * math.log(p,b)
    return ent

def getInformationGain(tree):
    if tree.isTerminal: return 0
    return tree.getEntropy() - tree.childPositive.getEntropy()*len(tree.childPositive.samples)*1./len(tree.samples) - tree.chilNegative.getEntropy()*len(tree.childNegative.samples)*1./len(tree.samples)
def getInformationGain(samples,dichotomy, keyStatements, b = 2):
    samplesPos = []
    samplesNeg = []
    for sample in samples:
        if dichotomy.extractValue(sample):
            samplesPos.append(sample)
        else:
            samplesNeg.append(sample)
    return getBoolEntropy(samples,keyStatements,b) - getBoolEntropy(samplesPos,keyStatements,b)*len(samplesPos)*1./len(samples) - getBoolEntropy(samplesNeg,keyStatements,b)*len(samplesNeg)*1./len(samples)
        

def getOpposites(numStatements):
    '''list of -1*numState statements'''
    import statements
    opposites = []
    for statement in numStatements:
        opposites.append(statements.getStatement(statements.op_minus,[statement]))
    return opposites
def getPairedSums(numStatements):
    import statements
    numCombinations = []
    for statement1 in numStatements:
        for statement2 in numStatements:
            if statement1 == statement2:continue
            numCombinations.append(statements.get_statement(statements.op_sum,[statement1,statement2]))
    return numCombinations
def getDifferences(numStatements):
    import statements
    numCombinations = []
    for i in range(len(numStatements)):
        for j in range(i,len(numStatements)):
            numCombinations.append(statements.get_statement(statements.op_sum,
                                                            [statements[i],
                                                             statements.get_statement(statements.op_minus,[statements[j]])]))
    return numCombinations
def getCombinations(numStatements):
    import statements
    combinations = []
    for code in range(1,3**len(numStatements)):
        s = statements.statement()
        s.operation = statements.op_sum
        s.args = []
        minusCount = 0
        plusCount = 0
        for i in range(len(numStatements)):
            form = (code % (3**(i+1)))/(3**i)
            if form ==0: continue
            elif form ==1:
                plusCount +=1
                s.args.append(numStatements[i])
            else: #form ==2
                minusCount +=1
                s.args.append(statements.get_statement(statements.op_minus,numStatements[i]))
        if plusCount >= minusCount: 
            combinations.append(s)
            
            
    return combinations
def visualize(classi):
    '''displays the nodes of the classification given'''
    classi.depth = 1
    openList = [classi]
    while len(openList) !=0:
         cur =openList.pop(0)
         if not cur.isTerminal:
             print cur.depth, cur.classifier.toString(),cur.probability
             cur.childNegative.depth = cur.depth+1
             cur.childPositive.depth = cur.depth+1
             openList.append(cur.childNegative)
             openList.append(cur.childPositive)
         else: print cur.depth,'[end]',cur.probability
    