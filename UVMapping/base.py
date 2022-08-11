import bpy
from .. import taichi as ti


samples : ti.Matrix = None
''' shape = (1,sampleNums) (1,2)
    [[ [0,0], : u
       [1,0]  : v
          ],
    [  [0,0],
       [1,0]
          ],
    ...
         ]          

'''

@ti.kernel
def reRandSamplesMaterixInstance(sampleNums : ti.uint16):
   samples = ti.Matrix.field(n= 2,m= 1,dtype=ti.f32,shape=(1,sampleNums))


floatingInterval : int = 1024


@ti.kernel
def setFloatingInterval(value : int):
   if floatingInterval != 1024:
       floatingInterval = value



@ti.kernel
def fillSamples():
   for ind in ti.grouped(samples):
       
       samples[ind][0,0] = ti.random(dtype= ti.f32)
       # u
       samples[ind][0,1] = 1 - samples[ind][0,0] -samples[ind][0,0]/floatingInterval
       # v

      
   




@ti.func
def reRandPoint(point0 : ti.Matrix,point1 : ti.Matrix,point2: ti.Matrix,u ,v) -> ti.Matrix:
      '''point shape = (3,1) , u and v is float32 
         Trigono metric parameter equations
         "p = v * b + u * c + (1 - v - u) * a"
         
         
         use point0(a) as root : 
         point1(b) use v
         point2(c) use u 
         p is result
       
      '''
      return point1 * v + point2 * u + (1 - u - v) * point0
