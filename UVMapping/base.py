import bpy
from .. import taichi as ti


samples : ti.Matrix = None
''' shape = (1,2) * sampleNums '''

@ti.kernel
def reRandSamplesMaterixInstance(sampleNums : ti.uint16):
   samples = ti.Matrix.field(n= 1,m= 2,dtype=ti.f32,shape=(sampleNums,1))


floatingInterval : ti.uint16 = 1024


@ti.kernel
def setFloatingInterval(value : ti.uint16):
   if floatingInterval != 1024:
       floatingInterval = value



@ti.kernel
def fillSamples():
   for ind in ti.grouped(samples):
       asix = ti.random(dtype=ti.f32) * ti.f32(floatingInterval / 65535)
       samples[ind][0,0] = ti.random(dtype= ti.f32)
       if samples[ind][0,0] > 0.50:
          samples[ind][0,1] = 0.50 - (samples[ind][0,0] - 0.50)
          samples[ind][0,1] = ti.random(dtype= ti.f32)

      
    




@ti.func
def reRandPoint(point0 : ti.Matrix,point1 : ti.Matrix,point2: ti.Matrix,u : ti.f32,v :ti.f32) -> ti.Matrix:
      '''point shape = (3,1)
         Trigono metric parameter equations
         "p = v * b + u * c + (1 - v - u) * a"
         
         
         use point0(a) as root : 
         point1(b) use v
         point2(c) use u 
         p is result
       
      '''
      return point1 * v + point2 * u + (1 - u - v) * point0
