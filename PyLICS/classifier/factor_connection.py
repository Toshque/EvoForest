import statements
#import copy


class connectionRecord:
    '''everything for a link between 2 statements'''
    def __init__ (self,state1, state2, bothTrue=0, bothFalse=0, trueFalse=0, falseTrue=0,
                  normalizerPositive=0,normalizerNegative = 0):
        self.statement1 = state1
        self.statement2 = state2
        self.bothTrue = bothTrue
        self.bothFalse = bothFalse
        self.falseTrue = falseTrue
        self.trueFalse = trueFalse
        self.normalizerPositive = float(normalizerPositive)
        self.normalizerNegative = float(normalizerNegative)

        self.strength = 0.0
    def update(self,sample,calculateAfterwards = True):
        '''process a sample'''
        w = sample._weight
        if self.statement2.extractValue(sample) == True:
            if self.statement1.extractValue(sample) == True:
                self.bothTrue +=w
                self.normalizerPositive +=w
            elif self.statement1.extractValue(sample) == False:
                self.falseTrue +=w
                self.normalizerPositive +=w
            else:raise ValueError, 'Non-boolean value!'
            
        elif self.statement2.extractValue(sample) == False:
            if self.statement1.extractValue(sample) == True:
                self.trueFalse +=w
                self.normalizerNegative +=w
            elif self.statement1.extractValue(sample) == False:
                self.bothFalse +=w
                self.normalizerNegative+=w
            else: raise ValueError, 'Non-boolean value!'
        else: raise ValueError, 'Non-boolean value!'
        if calculateAfterwards: self.calculate()
    def calculate(self):
        '''returns the total strength(sum/2) of a connection'''
        rslt = (self.getPositiveStrength()+ self.getNegativeStrength())/2
        self.strength = rslt     
        return rslt
    def getPositiveStrength(self):
        ''' bothTrue - falseTrue, normalized'''
        if self.normalizerPositive !=0: return (self.bothTrue - self.falseTrue)/ (self.normalizerPositive)
        return 0.0
    def getNegativeStrength(self):
        '''bothFalse - trueFalse, normalized'''
        if self.normalizerNegative !=0: return (self.bothFalse - self.trueFalse)/(self.normalizerNegative)
        return 0.0
    def processSamples(self,samples):
        '''processes the selected list of samples'''
        for smpl in samples: self.update(smpl)
        
        
        
        
        
        
import helpers
def getBestLink(keyStates,samples,boolStates,numStates=[],needOriginStatement = False):
    '''returns the best link - statement or record.'''
    if len(samples)==0:
        return (False,False) if needOriginStatement else False
    maxval =0.;#IG cannot be less than 0. If equal, return False
    bestState = None
    for state in boolStates:
        strength = helpers.getInformationGain(samples,state,keyStates)
        if strength > maxval:
            maxval = strength
            bestState = state

    originOfBest = bestState
    numRecordDict = {getBestLinkOverDiap(nstate,keystate,samples,True):nstate for keystate in keyStates for nstate in numStates}
    numRecordSet = numRecordDict.keys()
    for numRec in numRecordSet:
        strength = helpers.getInformationGain(samples,numRec.statement1,keyStates)
        if strength > maxval:
            maxval = strength
            originOfBest = numRecordDict[numRec]
            bestState = numRec.statement1
                    
    if bestState == None: 
        return (False,False) if needOriginStatement else False
    return (bestState, originOfBest) if needOriginStatement else bestState

      
      
      
def getBestLinkOverDiap(valueStatement,statement2, samples,needRecord = False):
    '''returns the best moreThan statement (valueStatement more than const) to classify statement2 in samples list'''
    valsSorted = []
    valdict = {}
    secondBoolVals = []


    for sample in samples:
        value = valueStatement.extractValue(sample)
        valdict[value] = sample
        for i in range( len(valsSorted) ):
            if value < valsSorted[i]:
                valsSorted.insert(i,value)
                secondBoolVals.insert(i,statement2.extractValue(sample))
                break
        else: 
            valsSorted.append(value)
            secondBoolVals.append(statement2.extractValue(sample))

    initial = connectionRecord(statements.get_moreThan(valueStatement,valsSorted[0]-0.1),statement2)
    initial.processSamples(samples)
    both_true = both_true_best = initial.bothTrue
    both_false = both_false_best = initial.bothFalse
    trueFalse = trueFalse_best = initial.trueFalse
    falseTrue = falseTrue_best = initial.falseTrue
    normalizerPositive = initial.normalizerPositive
    normalizerNegative = initial.normalizerNegative
    def getCurStrength():
        '''internal function -> simplified getConnectionStrength'''
        rslt =0.0
        if normalizerPositive != 0: rslt +=(both_true - falseTrue)/(2.0*normalizerPositive)
        if normalizerNegative != 0: rslt+= (both_false - trueFalse )/(2.0*normalizerNegative)
        return rslt        

    bestStrength =  getCurStrength()
    bestValueIndex = -1


    for i in range(len(valsSorted)):
        w = valdict[valsSorted[i]]._weight
        if secondBoolVals[i] == True:
            both_true -=w
            falseTrue +=w
        else: #st2 gives false
            both_false +=w
            trueFalse -=w
        if i == len(valsSorted)-1 or valsSorted[i] != valsSorted[i+1]:                
            strength =getCurStrength()
            if abs(strength ) > abs(bestStrength):
                bestStrength = strength
                bestValueIndex = i
                both_true_best = both_true
                both_false_best = both_false
                falseTrue_best = falseTrue
                trueFalse_best = trueFalse

    bestVal = valsSorted[bestValueIndex]
    if bestValueIndex != len(valsSorted)-1 and bestValueIndex !=-1:
        bestVal = 0.5*bestVal + 0.5*valsSorted[bestValueIndex+1]
    bestStatement = statements.get_moreThan(valueStatement,bestVal)

    if needRecord:
        rec = connectionRecord(bestStatement,statement2,falseTrue_best,trueFalse_best,both_false_best,both_true_best,
                             normalizerPositive,normalizerNegative)
        rec.strength = abs(bestStrength)
        return rec
        
    return bestStatement
                
    
