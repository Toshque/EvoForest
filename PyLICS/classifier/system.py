# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 22:43:23 2013

@author: sasha_000
"""
#it was noticed, that first classification takes much time on calculating numeric samples.
#it is useful to keep the candidates from the search.
import helpers
import statements
import treeNode
import factor_connection
import copy
import random
import time
from chromo import chromo

class system:
    def __init__(self,keyParams,boolParams, numParams, samples, samplesCount, nodesCount,attrsAvgPerTree, majorant = False, logWriter = None):
        '''the LICS itself'''
        '''reverse keyparams pls!'''
        self.boolParams = boolParams
        self.numParams = numParams
        self.keyParams = keyParams
        self.keyStatements = [ statements.get_statement(statements.op_takeValue,p) for p in keyParams]
        self.boolStatements = [ statements.get_statement(statements.op_takeValue,p) for p in boolParams]
        self.numStatements = [ statements.get_statement(statements.op_takeValue,p) for p in numParams]
        
        self.maxSamplesCount = samplesCount
        self.maxNodesCount = nodesCount
        self.maxAttrsCount = 0
        self.maxAvgAttrsPerTree = attrsAvgPerTree

        self.currentNodesCount = 0
        self.currentSamplesCount = 0 #not unique samples, but sample inclusions.
        self.currentAttrsCount = 0 #same

        self.isMajorant = majorant
        self.writeLog = False
        self.writeDump = False

        self.treesPool = set()#set chromo
        self.samplesPool = {sample:set() for sample in samples}#dict sample:trees with this sample.
        self.attrsPool = {attr:set() for attr in self.numStatements}

        
    def setLogWriter(self,logWriter):
        ''' set helpers.logWriter instance to collect all the metainfo of the system'''
        self.logWriter = logWriter
        self.writeLog = True
    def setDumpWriter(self,logWriter):
        ''' set helpers.logWriter instance to collect treespoul dumps once a round'''
        self.dumpWriter = logWriter
        self.writeDump = True
    def initialise(self):
        '''create initial pool of trees'''
        rateTrees = .3
        baseFitnessForIdealTree = 1


        if self.writeLog:
            self.logWriter.writeLine('starting initialisation')
            self.logWriter.timeMarker('init',False)
        samplesPerTree = int(round(self.maxSamplesCount/(rateTrees*self.maxNodesCount)+0.49))
        nodesPerTree = int(1/rateTrees)
        countTrees = int(self.maxNodesCount*rateTrees)
        self.maxAttrsCount= countTrees
        #ALARMA!! may need some details for samples/statements pools once they're implemented
        for i in range(countTrees):
            newCh = chromo(self,
                           set(helpers.proportionalrandom(self.samplesPool.keys(),lambda x:1,min(samplesPerTree,len(self.samplesPool)))) ,
                           self.boolStatements,
                           self.numStatements,
                           1)
            for i in range(nodesPerTree):
                if not newCh.expandBestNode():
                    break
            if newCh.numNodes ==0:
                continue
            newCh.fitness = helpers.getSuccessProbability(newCh,self.samplesPool.keys())*baseFitnessForIdealTree
            self.currentNodesCount+= newCh.numNodes
            self.currentSamplesCount+=len(newCh.samples)
            self.currentAttrsCount += len(newCh.boolStatements)+len(newCh.numStatements)
            self.treesPool.add(newCh)
            for sample in newCh.samples:
                self.samplesPool[sample].add(newCh)
        for sample in self.samplesPool.keys():
            if len(self.samplesPool[sample])==0:
                del self.samplesPool[sample]
        if self.writeLog:
            self.logWriter.timeMarker('init')
            self.logWriter.writeLine('init phase end.', len(self.treesPool),'trees created with',
                                     nodesPerTree,'nodes and',samplesPerTree,'samples each')
            

    def manageAttrs(self):
        
        extensionPoolCapacityRate = .2

        self.maxAttrsCount = self.maxAvgAttrsPerTree*len(self.treesPool)

        if self.writeLog:
            self.logWriter.writeLine( '\nManaging attrs. Initial attrs count = ',self.currentAttrsCount,'/',self.maxAttrsCount)
            self.logWriter.timeMarker('manageAttrs',False)


        extensionSequence = helpers.proportionalrandom(self.treesPool,lambda x: x.fitness / x.lenStatements(),max(int(extensionPoolCapacityRate*self.maxAttrsCount), 0))#(self.maxAttrsCount*expandedPoolCapacityRate-self.currentAttrsCount)
        if self.writeLog:
            self.logWriter.writeLine('Extension sequence length = ', len(extensionSequence))

        while len(extensionSequence)!=0:
            count=0
            elem = extensionSequence[-1]
            while extensionSequence[-1] == elem:
                extensionSequence.pop()
                count+=1
                if len(extensionSequence) ==0:
                    break;
            trueCount = elem.expandBestStates(count)
            self.currentAttrsCount+=trueCount

        deletionSequence = helpers.proportionalrandom(self.treesPool,
                                                      lambda x: x.lenStatements()/x.fitness, 
                                                      max(0,self.currentAttrsCount- self.maxAttrsCount ))
        if self.writeLog:
            self.logWriter.writeLine('Deletion sequence length = ', len(deletionSequence))
        
        _s=0
        while len(deletionSequence) !=0:
            count = 0
            elem = deletionSequence[-1]
            while deletionSequence[-1] == elem:
                deletionSequence.pop()
                count+=1
                if len(deletionSequence) ==0:
                    break;
            outcome, delSequence = elem.removeWorstStates(count)
            if outcome:
                self.currentAttrsCount -= count #if an entire tree is removed, the same is done inside removeTree method.

            else:
                self.removeTree(elem)
                _s+=1

        if self.writeLog:
            self.logWriter.writeLine( _s,' trees removed due to zero attrs')
            self.logWriter.timeMarker('manageAttrs')
            self.logWriter.writeLine( 'OnAfterSubStep attrs count = ',self.currentAttrsCount,'/',self.maxAttrsCount)
            self.logWriter.writeLine( 'End of attrs management.\n')

    def updateWithSample(self,sample,baseSampleImportance = .1):
        '''add a sample into the samples list and into the tree structure, returns a list of trees who misclassified the sample'''

        
        misclassified = set()
        for tree in self.treesPool:
            rDict = tree.classify(sample)
            if not helpers.isCorrectForSample(tree,sample):
                misclassified.add(tree)
            
        for tree in self.treesPool:
            if tree in misclassified:
                tree.fitness -= baseSampleImportance/(len(misclassified))
            else:
                tree.fitness += baseSampleImportance/(len(self.treesPool) - len(misclassified))

                

        return misclassified
        

        #ALARMA!! fitness functions are NOT normalised. at all. maybe tis better to normalise(instead or in addition)

    def processSamples(self,samples, sumAdditionRates = 5.):
        """processes a list of samples"""
        

        for sample in samples:
            self.updateWithSample(sample,sumAdditionRates/len(samples))
            self.samplesPool[sample] = set()
        
        treeseq = helpers.proportionalrandom(self.treesPool,
                                                      lambda x:x.fitness/len(x.samples),
                                                      int(round(sumAdditionRates*self.maxSamplesCount)))
        
        while len(treeseq) !=0:
            count = 0
            elem = treeseq[-1]
            while treeseq[-1] == elem:
                treeseq.pop()
                count+=1
                if len(treeseq) ==0:
                    break;
            count = min(count, len(samples))
            self.currentSamplesCount += count
            for samp in helpers.proportionalrandomNoRep(samples,lambda x:1,count):#WHY THE FUCKING FUCK DOES lambda x:<sum of fitnesses of trees failed> result in drops?!
                elem.addSample(samp)
                self.samplesPool[samp].add(elem)

        for sample in samples:
            if len(self.samplesPool[sample])==0:
                del self.samplesPool[sample]


    def fullLoop(self,samples=[]):
        '''process sample, than update the population'''

        if self.writeLog:
            self.logWriter.writeLine('New loop')
            self.logWriter.timeMarker('loop',False)

            self.logWriter.timeMarker('ProcessSamples',False)
        

        self.processSamples(samples)

            

        if self.writeLog:
            self.logWriter.timeMarker('ProcessSamples')
            self.logWriter.writeLine('Samples processed')

        self.manageTrees()
        self.manageAttrs()
        self.manageSamples()

        #witchhunt area
        #         ---
        #    -------------
        # -------  I  -------
        #    -------------
        #         ---
        #Beware the alien. The mutant. The heretic.
        for tree in self.treesPool:
            assert tree.numNodes != 0
            assert len(tree.samples)!=0
            for state in tree.stateUseDict:
                if state not in tree.boolStatements and state not in tree.numStatements:
                   assert len(tree.stateUseDict[state])!=0
        for sample in self.samplesPool:
            assert len(self.samplesPool[sample])!=0
        assert sum(len(self.samplesPool[i]) for i in self.samplesPool) == self.currentSamplesCount
        assert sum(i.numNodes for i in self.treesPool) == self.currentNodesCount
        assert sum(i.lenStatements() for i in self.treesPool) == self.currentAttrsCount
        for tree in self.treesPool:
            assert sum(len(tree.stateUseDict[state])for state in tree.stateUseDict) == tree.numNodes
        if self.writeLog:
            self.logWriter.writeLine('assertions passed')
        #end of witchhunt area
        
        avgFitness = sum(i.fitness for i in self.treesPool)/len(self.treesPool)
        
        for tree in self.treesPool:
            tree.fitness /= avgFitness

        if self.writeDump:
            self.dumpWriter.writeLine('\nNew round')
            for tree in self.treesPool:
                tree.logState(self.dumpWriter)



        if self.writeLog:
            self.logWriter.writeLine( 'max fitness:', max(i.fitness for i in self.treesPool) )
            self.logWriter.writeLine('avg fitness:', sum(i.fitness for i in self.treesPool)/len(self.treesPool))
            self.logWriter.writeLine('min fitness:', min(i.fitness for i in self.treesPool))
            self.logWriter.timeMarker('loop')
            self.logWriter.writeLine('loop end')

                
    def manageTrees(self):
        ''' update the pool'''
        recombinationRate = .025
        expandedPoolCapacityRate = 1.2
        if self.writeLog:
            self.logWriter.writeLine( '\nManaging trees pool. Initial nodes count = ', self.currentNodesCount,'/',self.maxNodesCount, ', trees count = ',len(self.treesPool))
            self.logWriter.timeMarker('manageTrees',False)

            self.logWriter.timeMarker('filterNegFitness',False)


        #remove all trees with their fitness <=0
        _s = 0
        for i in copy.copy(self.treesPool):
            if i.fitness <=0:#better be a deadline. check if this one is ever reached
                self.removeTree(i)
                _s+=1
        if self.writeLog:
            self.logWriter.timeMarker('filterNegFitness')
            self.logWriter.writeLine(_s,' trees removed due to negative fitness')

            self.logWriter.writeLine('\nRecombination phase')
            self.logWriter.timeMarker('recombination',False)



        _s = 0
        # add some new trees
        mutationSequence = helpers.proportionalrandom(self.treesPool,lambda x:(x.fitness),int(self.maxNodesCount*recombinationRate*2))
        if self.writeLog:
            self.logWriter.writeLine('Recombination phase: sequence len =',len(mutationSequence))



        random.shuffle(mutationSequence)
        #ALARME!!actual mutation for trees may be implemented either here or separately. or not implemented due to it's simulated by all the alterations with samples and nodes.
        while len(mutationSequence)>1:
            self.recombine(mutationSequence.pop(),mutationSequence.pop())
            _s+=1

        if self.writeLog:
            self.logWriter.timeMarker('recombination')
            self.logWriter.writeLine('End of recombination phase')

            self.logWriter.writeLine('\nExpansion phase')
            self.logWriter.timeMarker('expansion',False)

        #expand nodes up to maximal nodescount times expandedPoolCapacityRate (actually less due to absense of repetitions),
        # prioritised by tree fitness times expected benefit from expansion
        expandees = set(helpers.proportionalrandom(self.treesPool,lambda x:x.fitness*x.getBestReplacementPotential(),max(int((self.maxNodesCount*expandedPoolCapacityRate-self.currentNodesCount)), 0)))
        if self.writeLog:
            self.logWriter.writeLine( 'Expansion phase: sequence len =',len(expandees))
        for tree in expandees:
            if tree.expandBestNode():
                self.currentNodesCount+=1
        
        if self.writeLog:
            self.logWriter.timeMarker('expansion')
            self.logWriter.writeLine('End of expansion phase')

            self.logWriter.writeLine('\nPruning phase')
            self.logWriter.timeMarker('pruning',False)



        #remove up to all nodes above nodescount(actually less due to possibility that trees have less nodes than tis demanded to remove)
        # of least effective nodes in terms of nodes per fitness, remove empty trees
        reducees = helpers.proportionalrandom(self.treesPool,lambda x:x.numNodes/(x.fitness),max(self.currentNodesCount - self.maxNodesCount,0))
        if self.writeLog:
            self.logWriter.writeLine('Pruning phase: sequence len =',len(reducees))
            
        _s=0
        for tree in reducees:
            if tree in self.treesPool:
                
                if tree.pruneWorstNode():
                    self.currentNodesCount-=1 #if pruning fails, -1 node is done in removeTree
                else:
                    _s+=1
                    self.removeTree(tree)

        if self.writeLog:
            self.logWriter.writeLine( _s,' trees removed in pruning phase')
            self.logWriter.timeMarker('pruning')
            self.logWriter.writeLine('End of pruning phase')


        if self.writeLog:
            self.logWriter.timeMarker('manageTrees')
            self.logWriter.writeLine( 'OnAfterStep nodes count = ', self.currentNodesCount,', trees count = ',len(self.treesPool))
            self.logWriter.writeLine( 'End of tree management.\n')

    def removeTree(self,tree):
        self.treesPool.remove(tree)
        for sample in tree.samples:            
            self.samplesPool[sample].remove(tree)
            if len(self.samplesPool[sample])==0:
                del self.samplesPool[sample]
        self.currentNodesCount -= tree.numNodes
        self.currentSamplesCount-= len(tree.samples) #this list is NOT affected by the preceding loop.
        self.currentAttrsCount -= tree.lenStatements()

    def manageSamples(self):
        '''samples removal from trees (proportional to len(tree.samples)/tree.fitness) on exceeding maximal count, as well as [planned] recombination and spreading'''
        #ALARME!! try clustering here. may be good to cluster pairs with p ~ distance_between_samples/sum_of_importances but distance must be measured in terms of STATEMENTS of STATEMENT POOL proportionally to their IMPORTANCE... maybe
        #ALARME!! a place for spreading of existent samples, IF IT IS NECCESARY given that they spread via tree recombination
        #ALARME!! it may happen that a rubbish sample is kept cause it happened to be in one good chromo's list, test it and mb fix it somehow. p.e. expand 'good' samples in proportion to their fitness/len(self.samplesPool[sample]), but not to the 'best' nodes as won't fix the initial problem (mb uniformly?)
        
        if self.writeLog:
            self.logWriter.writeLine( '\nManaging samples. Initial samples count = ',self.currentSamplesCount,'/',self.maxSamplesCount)
            self.logWriter.timeMarker('manageSamples',False)


        deletionSequence = helpers.proportionalrandom(self.treesPool,
                                                      lambda x: len(x.samples)/x.fitness, 
                                                      max(0,self.currentSamplesCount- self.maxSamplesCount ))
        if self.writeLog:
            self.logWriter.writeLine('Deletion sequence length = ', len(deletionSequence))
        
        _s=0
        while len(deletionSequence) !=0:
            count = 0
            elem = deletionSequence[-1]
            while deletionSequence[-1] == elem:
                deletionSequence.pop()
                count+=1
                if len(deletionSequence) ==0:
                    break;
            outcome, delSequence = elem.removeSamples(count)
            if outcome:
                self.currentSamplesCount -= count #if an entire tree is removed, the same is done inside removeTree method.
                for sample in delSequence:
                    self.samplesPool[sample].remove(elem)
                    if len(self.samplesPool[sample])==0:
                        del self.samplesPool[sample]

            else:
                self.removeTree(elem)
                _s+=1
            

        if self.writeLog:
            self.logWriter.writeLine( _s,' trees removed due to zero samples')
            self.logWriter.timeMarker('manageSamples')
            self.logWriter.writeLine( 'OnAfterStep samples count = ',self.currentSamplesCount,'/',self.maxSamplesCount)
            self.logWriter.writeLine( 'End of samples management.\n')
                
                                
    def recombine(self,mother,father):
        '''adressing parential nodes as mather and father is no more stupid than calling your own parents "parent #" '''
        minNodesCount = 1

        #alarma might need to alter recombination here, ESPECIALLY statements

        newCh = chromo(self,set(list(mother.samples)+list(father.samples)),
                       set(list(mother.boolStatements)+list(father.boolStatements)),
                       set(list(mother.numStatements)+list(father.numStatements)),
                       1)#(mother.fitness+father.fitness)/2)

        for i in range(max(int((mother.numNodes+father.numNodes)/2),minNodesCount)):
            if not newCh.expandBestNode():
                if newCh.numNodes < minNodesCount:
                    return False
                break

        self.treesPool.add(newCh)
        for sample in newCh.samples:
            self.samplesPool[sample].add(newCh)
        self.currentNodesCount+= newCh.numNodes
        self.currentSamplesCount += len(newCh.samples)
        self.currentAttrsCount += len(newCh.boolStatements) + len (newCh.numStatements)
        return True



    def getSampleFitness(self,sample):
        '''calcuate sample fitness as an average fitness of all trees using this sample. 
        oath(23.10,02.05.2014): in future, it would be more natural to design decentralised samples management via recombination AND links between trees... not so?'''
        return sum(i.fitness for i in samplesPool[sample])/float(len(samplesPool[sample]))


    def classify(self,sample,threshold = 0,maxCount = -1):  
        ''' majorant classification of sample. might need to add support of quick classification later(like choosing best N trees and using ony em)'''
        assert len(self.treesPool)!=0
        states = tuple({i:0 for i in self.keyStatements}.keys()) #states in order of hash. y not just tuple(set(em))? dunno, checkit
        options = dict()

        pool = list(self.treesPool)
        if maxCount >0:
            pool.sort(key = lambda x: x.fitness,reverse = True)
            pool = pool[:maxCount]

        for ch in pool:
            if ch.fitness < threshold: continue
            r = tuple(ch.classify(sample).values())
            if r not in options:
                options[r] = 0
            options[r] += ch.fitness
        maxOpt = None
        maxVal = -float('inf')
        for option in options:
            val = options[option]
            if val>maxVal:
                maxVal = val
                maxOpt = option
        return {states[i]:maxOpt[i] for i in range(len(maxOpt))}


        

        
        


