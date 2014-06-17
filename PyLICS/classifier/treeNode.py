# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 21:42:50 2013

@author: sasha_000
"""
import helpers
class treeNode:
    def __init__(self,samples,keyStatements,majorant = False):
        '''a recursive decision tree class'''
        self.isTerminal = True
        self.isMajorant = majorant
        self.dichotomy = None
        self.samples = set(samples)
        self.keyStatements = keyStatements
        self.updated = False
        self.calculateOutput()
    def expand(self,dichotomy):
        '''extend the classification by spliting this node with a given dichotomy'''
        self.dichotomy = dichotomy
        posSamples = set()
        negSamples = set()
        for sample in self.samples:
            if dichotomy.extractValue(sample):
                posSamples.add(sample)
            else:
                negSamples.add(sample)
        self.childPositive = treeNode(posSamples,self.keyStatements,self.isMajorant)
        self.childNegative = treeNode(negSamples,self.keyStatements,self.isMajorant)
        self.isTerminal = False
    def classify(self,sample):
        '''Classify a sample according to this classification rules'''
        if not self.isTerminal:
            cls = self.dichotomy.extractValue(sample)
            if cls: return self.childPositive.classify(sample)
            else: return self.childNegative.classify(sample)
        else:
            return self.result
    
    def addSample(self,sample):
        self.samples.add(sample)
        if not self.isTerminal:
            if self.dichotomy.extractValue(sample):
                self.childPositive.addSample(sample)
            else:
                self.childNegative.addSample(sample)
        self.updated = False
    def removeSample(self,sample):
        self.samples.remove(sample)
        if not self.isTerminal:
            if self.dichotomy.extractValue(sample):
                self.childPositive.removeSample(sample)
            else:
                self.childNegative.removeSample(sample)
        self.updated = False

    def calculateOutput(self):
        '''updates result and the entropy of a node'''
        if self.updated:
            return self.result
        
        if not self.isMajorant:
            fchoose = helpers.getAverage
        else:
            fchoose = helpers.getMajorant
        self.result = fchoose(self.keyStatements,self.samples)
        self.entropy = helpers.getBoolEntropy(self.samples,self.keyStatements)
        self.updated = True
        return self.result
    def getEntropy(self):
        if not self.updated:
            self.calculateOutput()
        return self.entropy
    def getInformationGain(self):
        '''information gain of a given dichotomy for the last update'''
        assert (not self.isTerminal)
        return helpers.getInformationGain(self) 
    def visualise(self,encoder = None):
        classi = self
        if self.isTerminal:
            return ""
        resString = ""
        classi.depth = 1
        openList = [classi.childNegative,classi.childPositive]
        resString+=( classi.depth*2*' '+'IF'+ classi.dichotomy.toString().replace('op_','')+':'+'\n')
        classi.childPositive.depth =2
        classi.childPositive.pos = True
        classi.childNegative.depth =2
        classi.childNegative.pos = False
        while len(openList) !=0:
             cur =openList.pop(len(openList)-1)
             if cur.pos:
                 prefix = 'THAN '
             else:
                 prefix = 'ELSE '
             if  not cur.isTerminal:
                 statement = cur.dichotomy.toString()
                 resString+= (cur.depth*2*' '+prefix+'IF'+ statement.replace('op_','')+':'+'\n') #until 5.4.2014 there was +str(cur.result) before +':'
                 cur.childNegative.depth = cur.depth+1
                 cur.childPositive.pos = True
                 cur.childPositive.depth = cur.depth+1
                 cur.childNegative.pos = False
                 openList.append(cur.childNegative)
                 openList.append(cur.childPositive)
             else:
                 res = {i.toString():cur.result[i] for i in cur.result}
                 if encoder != None:
                    try: 
                         res = encoder.decode(res)
                    except :pass
                 resString+= (cur.depth*2*' '+prefix+'result ='+str(res)+'\n')
        return resString



