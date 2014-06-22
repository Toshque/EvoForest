#INTERFACE: statement
class statement:
    '''statement class for classification'''
    operation = None
    args = None
    def extractValue(self,sample):
        return self.operation(self.args,sample)
    def __hash__(self):
        return self.toString().__hash__()
    def __eq__(self,other):
        return self.__hash__() == other.__hash__()
    def toString(self):
        arr = []
        for i in self.args:
            if type(i)  in (float,int,bool): arr.append(str(i))
            elif type(i) == str: arr.append(i)
            else: arr.append(i.toString())
        opstr = str(self.operation)
        return filter(lambda x: x not in ["'",'"'],(opstr[9:opstr.index('at 0x')]  +str(arr)))

import helpers


def get_takeValue(valueStr):
    '''takes a value with a specified name'''
    return get_statement(op_takeValue,valueStr)
def get_takeConstant(constant):
    return get_statement(op_takeConstant,constant)
def get_statement(operation,args):
    '''get statement with this operation and args'''
    assert operation not in {op_sum,op_mul}
    newsttmnt = statement()
    newsttmnt.operation = operation
    if type(args) != list: args = [args]
    newsttmnt.args = args
    return newsttmnt
def get_sum(argStatements):
    '''get statement, which is returning the sum of values of arg statements'''
    newsttmnt = statement()
    newsttmnt.operation = op_sum
    newsttmnt.args = list(set(argStatements)) #sort by hash
    return newsttmnt
def get_mul(argStatements):
    '''get statement, which is returning the sum of values of arg statements'''
    newsttmnt = statement()
    newsttmnt.operation = op_mul
    newsttmnt.args = list(set(argStatements)) #sort by hash
    return newsttmnt
def get_negation(argsttmnt):
    '''get the statement, which is only true when the arg is false and visa versa'''
    newsttmnt = statement()
    newsttmnt.args = [argsttmnt]
    newsttmnt.operation = op_negation
    return newsttmnt
def get_minus(argsttmnt):
    '''get the statement, which returns the original statement's value, multiplied by -1'''
    newsttmnt = statement()
    newsttmnt.args = [argsttmnt]
    newsttmnt.operation = op_minus
    return newsttmnt
def get_moreThan(argsttmnt,value):
    '''get a statement which is true, when argstatement's rslt is more than value'''
    cstatement = statement()
    cstatement.operation = op_takeConstant
    cstatement.args = [value]
    newsttmnt = statement()
    newsttmnt.operation = op_more
    newsttmnt.args = [argsttmnt,cstatement]
    return newsttmnt
def get_and(argst1,srgst2):
    newst = statement()
    newst.operation = op_and
    newst.args = [argst1,srgst2]
    return newst
def get_or(argst1,srgst2):
    newst = statement()
    newst.operation = op_or
    newst.args = [argst1,srgst2]
    return newst

def shift_comparsion(argsttmnt, delthaOfSecondArg): 
    '''adds deltha to the second arg of comparsion(moreThan, lessThan) statement'''
    argsttmnt.args[1].args[0]+=delthaOfSecondArg

def op_takeValue(args,sample):
    '''operation: take value with args[0] as name'''
    try:
        return getattr(sample,args[0]) #<- arg is a string. It's a statement elsewhere
    except:
        return False #if there's no data, than it's false <- by default

def op_takeConstant(args,sample):
    '''get args[0] value as a result'''
    return args[0]

def op_negation(args,sample):
    '''NOT(args[0])'''
    return not args[0].extractValue(sample)

def op_sum(args,sample):
    '''args[0]+args[1]+...'''
    return sum(i.extractValue(sample) for i in args)

def op_mul(args,sample):
    '''args[0]*args[1]'''
    return helpers.mul([i.extractValue(sample) for i in args])
def op_minus(args,sample):
    '''-1*args'''
    return -1*args[0].extractValue(sample)

def op_and(args,sample):
    '''args[0] and args[1]'''
    return args[0].extractValue(sample) and args[1].extractValue(sample)

def op_or(args,sample):
    '''args[0] or args[1]'''
    return args[0].extractValue(sample) or args[1].extractValue(sample)

def op_implication(args,sample):
    '''args[0] -> args[1]'''
    return not(args[0].extractValue(sample)) or args[1].extractValue(sample)

def op_equivalence(args,sample):
    '''args[0] == args[1]'''
    return args[0].extractValue(sample) == args[1].extractValue(sample)

def op_more(args,sample):
    '''args[0] > args[1]'''
    return args[0].extractValue(sample) > args[1].extractValue(sample)

def op_less(args,sample):
    ''' args[0] < args[1]'''
    return args[0].extractValue(sample) < args[1].extractValue(sample)

def op_function(args,sample): #<- function must be stored as args[0], and the args are args[1:len(args)]
    '''args[0](args[1:])'''
    vals = [arg.extractValue(sample) for arg in args[1:len(args)]]
    return args[0](vals)
    
