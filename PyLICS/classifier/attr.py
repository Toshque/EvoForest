class attr:
    """attribute record, fully compatible with all statement usages"""
    def __init__(self,operation,args,params):
        self.operation = operation #p.e. sin or linear combination or whatever
        self.args = args
        self.params = params
    def extractValue(self,sample):
        return self.operation(self.args,self.params,sample)
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
        return filter(lambda x: x not in ["'",'"'],(opstr[9:opstr.index('at 0x')]  +str(arr))+str(self.params))


import math
op_linearCombination = lambda args,params,sample: sum(args[i].extractValue(sample)*params[i] for i in range(len(params)))
def op_multiplication(args,params,sample):
    s = 1
    for i in range(len(params)):
        s*=args[i].extractValue(sample)**params[i]
    return s

op_power = lambda args, params, sample: params[0]**(args[0].extractValue(sample))
op_log   = lambda args, params, sample: math.log( params[0]**(args[0].extractValue(sample)),params[0])

op_polynomial = lambda args,params,sample: sum(params[i]*args[0]**i for i in range(len(params)))
