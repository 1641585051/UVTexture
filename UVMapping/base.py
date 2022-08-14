from typing import Any
import bpy
import mathutils
import taichi as ti


samples : ti.Matrix = None
''' shape = (1,sampleNums) (1,2)
    [[ [0,0], : u
       [0,1]  : v
          ],
    [  [0,0],
       [0,1]
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

      
   

def TrigonoMetricParameterEquations(a,b,c,u,v):
    '''  
         Trigono metric parameter equations
         "p = v * b + u * c + (1 - v - u) * a"
         
         
         use point0(a) as root : 
         point1(b) use v
         point2(c) use u 
         p is result
       
      '''
    return b * v + c * u + (1 - u - v) * a



@ti.func
def rePoint(point0  ,point1  ,point2 ,u : ti.f32 ,v : ti.f32) :
      '''point shape = (3,1) , u and v is float32 
         Trigono metric parameter equations
         "p = v * b + u * c + (1 - v - u) * a"
         
         
         use point0(a) as root : 
         point1(b) use v
         point2(c) use u 
         p is result
       
      '''
      return point1 * v + point2 * u + (1 - u - v) * point0



@ti.func
def LinearIntegrationFunc(k , x):
    return  (k * (1/2)) * (x **2)



@ti.func
def barycentr(o ,b ,c):

    '''o,a,b : (n,m) 
       [
         [],
         [],
         []
       ]
      Virtual 3D has no concept of density,so ignore it and set to 1

    '''

    v : ti.Matrix = (b - o)

    vK = v.normalized()

    u : ti.Matrix = (c - o)

    uK = u.normalized()

    # the center of gravity is calculated by integrals
    # func is LinearIntegrationFunc
                                                                                                                                       # integral 1 (o,b)
    vreposition : ti.Matrix = ti.Vector(arr =[[(LinearIntegrationFunc(k=vK[0,0],x=b[0,0]) - LinearIntegrationFunc(k=vK[0,0],x=o[0,0])) / v[0,0]],
                                              [(LinearIntegrationFunc(k=vK[0,1],x=b[0,1]) - LinearIntegrationFunc(k=vK[0,1],x=o[0,1])) / v[0,1]],
                                              [(LinearIntegrationFunc(k=vK[0,2],x=b[0,2]) - LinearIntegrationFunc(k=vK[0,2],x=o[0,2])) / v[0,2]]
                                             ]) # integ(1 * k*x) / integ(1) form [o,b] , Performed separately on x,y,z
    #still is  [ [],
    #            [],
    #            []]
   
   
    ureposition : ti.Matrix = ti.Vector(arr =[[(LinearIntegrationFunc(k=uK[0,0],x=c[0,0]) - LinearIntegrationFunc(k=uK[0,0],x=o[0,0])) / u[0,0]],
                                             [(LinearIntegrationFunc(k=uK[0,1],x=c[0,1]) - LinearIntegrationFunc(k=uK[0,1],x=o[0,1])) / u[0,1]],
                                             [(LinearIntegrationFunc(k=uK[0,2],x=c[0,2]) - LinearIntegrationFunc(k=uK[0,2],x=o[0,2])) / u[0,2]]
                                       ])
 
    vtem = vreposition - o 

    vend = vtem[0,0] / v[0,0]
    # Since it is a linear space, only one axis(x) is taken

    utem = ureposition - o

    uend = utem[0,0] / v[0,0]

    return rePoint(point0= o,point1= b,point2= c,u=uend,v= vend)
    # Returns the center of gravity via parametric equations

def makeUVVertMap(obj : bpy.types.Object,isContainsUVData : bool):
          '''if isContainsUVData is true ,reture map[int,mathutils.Vector]
             else return layer and map[int,int] vert index -> loop index
          
          '''

          bpy.context.active_object = obj
          meshMap = map()
          me = bpy.context.object.data
          uv_layer = me.uv_layers.active.data

          for poly in me.polygons:

             for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                if isContainsUVData:
                   meshMap[me.loops[loop_index].vertex_index] = me.loops[loop_index].uv
                else:
                   meshMap[me.loops[loop_index].vertex_index] = loop_index

          if isContainsUVData:
             return meshMap  
          else:
             return meshMap,uv_layer   
 