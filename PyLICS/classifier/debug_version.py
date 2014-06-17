# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 19:45:34 2013

@author: sasha_000
"""

# -*- coding: utf-8 -*-classi
import statements
import samples
import random
import math
#---------------------------------------------------------------------


slist = []
def createSample():
    A = math.cos(random.random()*math.pi - math.pi/2) #cos a
    B = random.random()*2 -1
    O = random.choice([False,False,False,False,True])
    C1 = random.choice([False,True])
    C2 = random.choice([False,True])
    G = random.choice([False,False,True])
    Li =  ((random.random()*2-1)**1)/2 +0.5
    L = [None]+ [Li -0.15 + random.random()*0.3 for i in range(4)]
    for i in range(1,5):
        if L[i] <0: L[i] = 0.
        elif L[i] >1: L[i] =1. 
    Lm = sum(L[1:5])/4 
    C = False
    R = True
    if O: 
        R=False
        C = True
    elif A<0.25:
        R = False
        if A<0.15:
            C =True
    elif max(L[1:5]) - min(L[1:5]) > 0.3:
        R = False
    elif Lm < 0.25:
        R = False
    elif C1:
        if Lm < 0.35:
            R = False
        elif C2 and (Lm <0.4):
            R = False
    elif G == True:
        if Lm > 0.65:
            R = False
        elif (not C1) and (not C2) and Lm >0.6:
            R = False
        elif max(L[1:5]) - min(L[1:5]) > 0.2:
            R = False

    elif  random.random() < 0.03:
        R = False
    if Lm<0.15:
        C = True
    
    
    return samples.sample(['A','B','O','C1','C2','G',
                           'L1','L2','L3','L4','R','C'],
                           [A,B,O,C1,C2,G,
                            L[1],L[2],L[3],L[4],R,C])
def createSample_prejudiced():

    A = 1
    B = random.random()*2 -1
    O = False
    C1 = False
    C2 = random.choice([False,True])
    G = False
    Li =  ((random.random()*2-1)**3)/2 +0.5
    L = [None]+ [Li -0.1 + random.random()*0.2 for i in range(4)]
    for i in range(1,5):
        if L[i] <0: L[i] = 0.
        elif L[i] >1: L[i] =1. 
    Lm = sum(L[1:5])/4 
    C = True
    R = True
    if O: 
        R=False
    elif A<0.25:
        R = False
    elif max(L[1:5]) - min(L[1:5]) > 0.3:
        R = False
    elif Lm < 0.25:
        R = False
    elif C1:
        if Lm < 0.35:
            R = False
        elif C2 and (Lm <0.4):
            R = False
    elif G == True:
        if Lm > 0.65:
            R = False
        elif (not C1) and (not C2) and Lm >0.6:
            R = False
    elif  random.random() < 0.03:
        R = False
    
    
    return samples.sample(['A','B','O','C1','C2','G',
                           'L1','L2','L3','L4','R','C'],
                           [A,B,O,C1,C2,G,L[1],L[2],L[3],L[4],R,C])


outer=[]
def check(classifier,keyStates,num,thr = 0):
    successes = 0
    for i in range(num):
        smpl = createSample()
        for i in range(len(keyStates)):
            if round(classifier.classify(smpl,thr)[keyStates[i]]) != keyStates[i].extractValue(smpl):
                    break

        else:successes +=1
    return successes

state0 = statements.get_statement(statements.op_takeValue,'A')
state1 = statements.get_statement(statements.op_takeValue,'B')
state2 = statements.get_statement(statements.op_takeValue,'O')
state3 = statements.get_statement(statements.op_takeValue,'C1')
state4 = statements.get_statement(statements.op_takeValue,'C2')
state5 = statements.get_statement(statements.op_takeValue,'G')
state6 = statements.get_statement(statements.op_takeValue,'L1')
state7 = statements.get_statement(statements.op_takeValue,'L2')
state8 = statements.get_statement(statements.op_takeValue,'L3')
state9 = statements.get_statement(statements.op_takeValue,'L4')
boolStatements = [state2,state3,state4,state5]
numStatements = [state0,state1,state6,state7,state8,state9]


slist = [createSample_prejudiced() for i in range(1000)]
numparams= ['A','B','L1','L2','L3','L4']
boolparams = ['O','C1','C2','G']
keyparams = ['R','C']
                                  
import time
import agent
t = time.time()
sys = agent.system(keyparams,boolparams,numparams,slist,6000,300,1000000)
keyStates =sys.keyStatements


import helpers
sysLog = helpers.logWriter()
sysDump = helpers.logWriter()

sys.setLogWriter(sysLog)
sys.setDumpWriter(sysDump)
def runSimulation(rounds = 100,tests = 500):
    sys.initialise()
    sysLog.printToConsole()
    num = tests
    flog = open("lastLog.log",'w')
    fdump = open("lastDump.log",'w')
    effi = check(sys,keyStates,num)
    print 'initial efficiency',effi*100. /num,'%','\n\n\n\n'
    for ri in range(rounds):
        sysLog.writeLine( '\n\n\n\nround #',ri)
        sysDump.writeLine('\n\n\n\nBeginning round #',ri)
        
        sys.fullLoop([createSample() for i in range(50)])
        effi1 = check(sys,keyStates,num)
        effi2 = check(sys,keyStates,num,1)
        sysLog.writeLine( 'efficiency(>0) = ',effi1*100. /num,'%')
        sysLog.writeLine( 'efficiency(>1) = ',effi2*100. /num,'%')

        sysLog.writeLine( 'End of round',ri)
    
        s = sysLog.readString()
        print s
        flog.write(s);  
        fdump.write(sysDump.readString())

        sysDump.removeOld()
        sysLog.removeOld() #remove me if you don't want logs to wipe after printed
        
    flog.close()
    fdump.close()
    
if __name__ == '__main__':
    runSimulation()