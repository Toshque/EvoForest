from wrapper import *
#debug section
print '!mark: test start'
sy = getSystem()
bit0 = Bitmap(width,height)
bit1 = Bitmap(width,height)
bit1.SetPixel(2,2,Color.White)
bit2 = Bitmap(width,height)
for i in range(width):
    for j in range(height):
        bit2.SetPixel(i,j,Color.White)


feedSampleToSystem(sy,bit0,3)
feedSampleToSystem(sy,bit1,2)
feedSampleToSystem(sy,bit2,1)
print '!mark: started to compose tree'
sy.compose()
print '!mark: finished composing tree'
print sy.samples
print sy.tree.visualise()

#buglist!!!: Aham. Also it seemed to break down on small number of existant samples.
#Also it's SLOW on 'compose' if amount of numstatements is too high. EXTREMELY  slow! find out a way to fix it! (forest approach?)
#there's a hypotesis of this encoder workin arright. dun' touch it.
print sy._injectedEncoder.decode(sy.tree.classify(sampleFromBitmap(bit0)))
print sy._injectedEncoder.decode(sy.tree.classify(sampleFromBitmap(bit1)))
print sy._injectedEncoder.decode(sy.tree.classify(sampleFromBitmap(bit2)))
