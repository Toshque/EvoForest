class sample:
    '''a sample class, extractable. Attributes are managed via setattr/getattr functions'''
    def __init__(self,names,args):
        self._weight = 1.#not the same ting as system.getSampleFitness(sample)
        for i in range(len(args)):
            setattr(self,names[i],args[i])
        
        
            
            
