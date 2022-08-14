
import sys
from this import d
from .base import rePoint
import bpy
import bmesh
import mathutils



from mars import tensor as ten 

import numpy as np
from bpy.types import Context

## this file not have UVMapping Base Operator ,only have Calculation operators
## base operator in UV_operators.UVTexture_OT_ObjectUVMapping ...

gl_back_data : ten.Tensor = None
'''gl_back_data only valid in one operation'''

gl_mesh_data : ten.Tensor = None
'''gl_mesh_data only valid in one operation'''




def updateDatas(context : Context,uvMappingObjectName : str,backGroundObjName :str):
     
      global gl_back_data
      gl_back_data = None

      global gl_mesh_data 
      gl_mesh_data = None 

      obj = context.scene.objects[context.scene.objects.find(uvMappingObjectName)]      

      backgroundObj = context.scene.objects[context.scene.objects.find(backGroundObjName)]  

      mesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(obj.to_mesh()) 

      objVerts : list[tuple[np.float32,np.float32,np.float32]] = list()
      objcount = len(mesh.verts)
      for i in range(objcount):
            ve = mesh.verts[i].co
            objVerts.append((ve.x,ve.y,ve.z))


      objarr = np.array(object= objVerts,dtype= np.float32).reshape(shape=(objcount,3))
      # ndarray shape (objcount,3)
      
      backMesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(backgroundObj.to_mesh()) 
      
      backVerts : list[tuple[np.float32,np.float32,np.float32]] = list()
      backcount = len(backMesh.verts)
      for i in range(backcount):
           ve = backMesh.verts[i].co
           backVerts.append((ve.x,ve.y,ve.z))

      backarr = np.array(object= backVerts,dtype= np.float32).reshape(shape=(backcount,3))
      # ndarray shape (backcount,3)

    
      gl_back_data = ten.tensor(data= objarr,gpu= True)
      gl_back_data.execute()

    
      gl_mesh_data = ten.tensor(data= backarr,gpu= True)
      gl_mesh_data.execute()


      backMesh.free()
      mesh.free()
       


class UVTExture_OT_UvMappingCalculateProjectionValue(bpy.types.Operator):

    bl_idname: str = 'object.calculateProjectionValue'  
    bl_label: str = 'get mapping project mesh data'

    uvMappingObjectName = bpy.props.StringProperty(name='uvMappingObjectName',default='None')

    backGroundObjName = bpy.props.StringProperty(name='backGroundObjName',default='None')

    isUseMultiStageSampling = bpy.props.BoolProperty(name='isUseMultiStageSampling',default=False)
 
    def check(self,context) -> bool:
      return (self.uvMappingObjectName != 'None' and self.backGroundObjName != 'None')

    def invoke(self, context, event):
       return super().invoke(context, event)

    def execute(self, context):   

      sampleNums = context.scene.uv_texture_output_config[list(context.scene.uv_texture_output_config.keys()).count() - 1].mappingSampleNums 

      from ..tools import gpuEnv
      
      datanpArr : np.ndarray = None

      ##    CUDA    ## 
      if gpuEnv.NVorAmd:

            # mars use cuda in gpu

            global gl_mesh_data
            global gl_back_data
            shapem = list(gl_back_data.shape)
            
            m :int = shapem[0]

            n :int = shapen[0]
          
            gl_mesh_data = ten.swapaxes(gl_mesh_data,axis1=0,axis2=1) 
            gl_mesh_data = ten.ravel(gl_mesh_data)
            gl_mesh_data = ten.tile(gl_mesh_data,(1,m))
            
            gl_mesh_data.execute()

            shapen = list(gl_mesh_data.shape)

            gl_back_data = ten.swapaxes(gl_back_data,axis1=0,axis2=1) 
            gl_back_data = ten.tile(gl_back_data,(n,1))

            gl_back_data.execute()

            '''
            gl_mesh_data as gm
            gl_back_data as gb

            gm.shape = (n,3)
            gb.shape = (m,3)   

            gm (n,3) -> (3,n)  ->      (3n,1)    ->     (3n,m)
                  swapaxes(.,(0,1))   ravel       tile(.,(1,m))    

            gb (m,3) ->       (3,m)        ->   (3n,m)
                        swapaxes(.,(0,1))      tile(.,(n,1)) 
            
            
            '''
            subten : ten.Tensor = ten.zeros(shape=(3* n,m),dtype= np.float32,gpu=True)
            ten.subtract(x1= gl_back_data,x2= gl_mesh_data,out=subten)

            subten.execute()
            # sub ten is subtract(gl_back_data,gl_mesh_data)
              
            xlist :list[ten.Tensor] = ten.hsplit(a=subten,indices_or_sections= 3)   
            
            newTen : ten.Tensor = ten.empty(shape=(1,3),dtype=np.float32,gpu=True)

            for xten in xlist:
              # xTen shape = (3,m)
              
              ten.exp2(x= xten,out= xten)
              xten.execute()
              disTen : ten.Tensor = ten.zeros(shape=(1,m),dtype=np.float32,gpu=True) 
              ten.sum(a= xten,axis=0,dtype=np.float32,out=disTen)
              disTen.execute()

              arr : np.ndarray = np.argsort(a= disTen.to_numpy(),axis=1,kind= 'mergesort')
              indList : ten.Tensor = ten.tensor(data= arr,dtype= np.float32,gpu= True)
              # (1,m)
              indList.execute()
              
              temten : list[ten.Tensor] = ten.vsplit(a= indList,indices_or_sections= ten.array([3,m -3]))     
              
              newTen = ten.hstack((newTen,temten[0]))

              newTen.execute()

            #newTen shape = (n,3)
            
            newt :ten.Tensor = ten.empty(shape= (3,3),dtype=np.float32,gpu=True)

            elements : list[ten.Tensor] = ten.hsplit(a=newTen,indices_or_sections= 1)
            for el in elements: 
              newElement = ten.tile(A= el,reps=3)
              ten.hstack((newt,newElement))
              newt.execute()
              # newt (3n,3)

            endData : ten.Tensor = ten.take(a= gl_back_data,indices=newt)
            endData.execute()
            # (3n,3) closest three point in back points

            mapdata : ten.Tensor = ten.zeros(shape= (3*n,1),dtype=np.float32,gpu=True)

            ten.take(a= gl_mesh_data,indices= 0 ,axis=1,out= mapdata)

            mapdata.execute() 
            #(3n,1) mesh point

            dataTen :ten.Tensor = ten.vstack((mapdata,endData))
            dataTen.execute()
            # [
            #   0 : mapdata (mesh)
            #   1 - 3 : endData (back)
            # ]
            
            datanpArr = np.ascontiguousarray(a= dataTen.to_numpy(),dtype=np.float32)
            # (3n,4)

       ## ---------------

      else:
       ##     AMD      ##
         pass



       ## ---------------   


     

      import taichi as ti
      from .import base  

      floatingInterval : int = context.scene.uv_texture_System_config.floatingInterval
      
      base.setFloatingInterval(floatingInterval) 

      
      spArr : np.ndarray = np.array(object= np.split(ary= datanpArr,indices_or_sections= 3,axis=1),dtype=np.float32)
      #  shape (3,4,n)

      materix : ti.MatrixField = ti.Matrix.field(n= 4,m=3,dtype= ti.float32,shape=(n,1))
      # [  [[00,10,20,    [[00,10,20,
      #      01,11,21,      01,11,21,
      #      02,12,22,      02,12,22, .....
      #      03,13,23]],    03,13,23]],          ]

      temNDa : ti.MatrixNdarray = ti.MatrixNdarray(n=4 ,m= 3,dtype=ti.f32,shape=(n,1))
      temNDa.from_numpy(arr=spArr)
      
      @ti.kernel
      def fullMaterix():
        for ind in ti.static(ti.grouped(materix)):
           
           materix[ind] = temNDa[ind[0],0]
           # materix (3,4)(n,1) so grouped -> ind = [0,0]/[1,0]/ ... [n,0]
           # ind[0] = 0/1/...n

      fullMaterix()

    
      base.reRandSamplesMaterixInstance(sampleNums= sampleNums)

      base.fillSamples()

      points : ti.MatrixField = ti.Matrix.field(n= 3,m= 1,dtype= ti.f32,shape=(n,sampleNums))
      # [[0,0], ..... n
      #  [0,1],
      #  [0,2]],
      #  .
      #  .
      #  .
      #  sampleNums

      @ti.kernel
      def RandPoints():
          for ind in ti.static(ti.grouped(materix)):
              # ind [0,0] / [1,0] ...
              back_point0 = [[materix[ind][0,1]],
                            [materix[ind][1,1]],
                            [materix[ind][2,1]]]
              back_point1 = ti.Vector([[materix[ind][0,2]],
                                       [materix[ind][1,2]],
                                       [materix[ind][2,2]]])
              back_point2 = ti.Vector([[materix[ind][0,3]],
                                       [materix[ind][1,3]],
                                       [materix[ind][2,3]]])

              # point shape  (1,3) n =3 m=1                          
                   
              for ind1 in ti.grouped(points):
                 if ind1[0] == ind[0]: # materix[n] and points[n]
                    
                    uv = base.samples[0,ind1[1]] 
                    # uv is not blender uv ,that is Trigono metric parameter equations uv parmeters
                    # (1,2)
                    points[ind1] = base.rePoint(
                                point0= back_point0,
                                point1= back_point1,
                                point2= back_point2,
                                u= uv[0,0],
                                v= uv[0,1]

                                )
                  
                  # get all random points to get normal

      RandPoints()
       

      result :ti.MatrixField = ti.Matrix.field(n=5,m=3,dtype=ti.f32,shape= (n,1))  
      # [[[mesh.x ,mesh.y ,mesh.z ],  [[mesh.x ,mesh.y ,mesh.z ], ..... n
      #   [bakeO.x,bakeO.y,bakeO.z],   [bakeO.x,bakeO.y,bakeO.z],
      #   [bake1.x,bake1.y,bake1.z],   [bake1.x,,bake1.y...]
      #   [bake2.x,bake2.y,bake2.z],   ...
      #   [u      ,v      ,      0]],  [u      ,v      ,      0]],
      #  
      #                                                               1 ]
       

      @ti.kernel
      def NormalRayCapture():
          for ind in ti.static(ti.grouped(materix)):

              mesh_point = [[materix[ind][0,0]],
                            [materix[ind][1,0]],
                            [materix[ind][2,0]]
                            ]
              back_point0 = [[materix[ind][0,1]],
                             [materix[ind][1,1]],
                             [materix[ind][2,1]]
                             ]
              back_point1 = [[materix[ind][0,2]],
                             [materix[ind][1,2]],
                             [materix[ind][2,2]]
                             ]
              back_point2 = [[materix[ind][0,3]],
                             [materix[ind][1,3]],
                             [materix[ind][2,3]]
                             ]

              dirmaterix = ti.Vector(arr= mesh_point,dt= ti.f32)
              materix0 = ti.Vector(arr= back_point0,dt=ti.f32)   
              # materix0 in [Trigono metric parameter equations] have parameter (1- u-v) and this less than zero
              
              materix1 = ti.Vector(arr= back_point1,dt= ti.f32)
              materix2 = ti.Vector(arr= back_point2,dt= ti.f32)
              
              
              dirReference : ti.Matrix = dirmaterix - materix0
              # dirReference use to have the normals generated by cross point to the 
              # side that is biased towards the mesh point

              var0 : ti.Matrix = materix1 - materix0
              var1 : ti.Matrix = materix2 - materix0
          
              normal : ti.Matrix = var1.cross(var0)

              if normal.dot(dirReference) < 0:
                 normal = normal * -1

              baryc : ti.Matrix = base.barycentr(o= materix0,b= materix1, c= materix2)

              dots :ti.Matrix = ti.field(dtype=ti.f32,shape=(1,sampleNums))

              for indPoints in ti.grouped(points):
               
                if indPoints[0] == ind[0]:
                   
                   for sampleInd in ti.static(ti.ndrange((0,sampleNums))):
                      
                      tem : ti.Matrix =  baryc - points[indPoints[0],sampleInd]
                      
                      othernor :ti.Matrix = mesh_point - points[indPoints[0],sampleInd]
                      
                      dots[1,sampleInd] = tem.dot(othernor) / ((tem[0,0]/ tem.normalized()[0,0]) * (othernor[0,0]/ othernor.normalized()[0,0]))
                 
              dots = ti.abs(arr=dots)

              for dotInd in ti.grouped(dots):
                 if dots[dotInd] == dots.min():
                     uv = base.samples[0,dotInd[1]] 
                     result[ind[0],0] = ti.Vector(
                           arr= [
                                 [mesh_point[0,0],mesh_point[0,1],mesh_point[0,2]],
                                 [back_point0[0,0],back_point1[0,1],back_point2[0,2]],
                                 [back_point1[0,0],back_point1[0,1],back_point1[0,2]],
                                 [back_point2[0,0],back_point2[0,1],back_point2[0,2]],
                                 [uv[0,0]         ,uv[0,1]         ,               0] 
                                ])

      
      NormalRayCapture()
 
      # Sample multiple times to improve accuracy 

      if gpuEnv.NVorAmd:

       
        ##     CUDA     ##
        array : np.ndarray = points.to_numpy()
        
        pointsformTaichi : ten.Tensor = ten.full(shape=array.shape,fill_value= array,dtype=np.float32)
        

        #(n, simpleNums,1,3)
        




        ## -----------------

      else:
        ##      AMD      ##





        ##------------------
        pass




      from ..lookMouse import lookMouse

      lookMouse.lookMouse()
        
      backgroundObj = context.scene.objects[context.scene.objects.find(self.backGroundObjName)]  

      backobjMap = base.makeUVVertMap(obj= backgroundObj,isContainsUVData= True)

      obj = context.scene.objects[context.scene.objects.find(self.uvMappingObjectName)]      
      
      meshMap,obj_layer = base.makeUVVertMap(obj= obj,isContainsUVData= False) 
      
      mesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(obj.to_mesh()) 
      
      backMesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(backgroundObj.to_mesh())

      barray = result.to_numpy()
      # (n,1,5,3)
      barray1 = np.squeeze(a= barray)
      # (n,5,3)

      def getIndex(mesh : bmesh.types.BMesh, point: mathutils.Vector):
        meshIndex : int = sys.maxsize
        for vert in mesh.verts:
             bvert : bmesh.types.BMVert = vert
             if bvert.co == point:
                 meshIndex = bvert.index
        return meshIndex

      bpy.context.active_object = obj
      
      for ind in range(barray1.shape[0]):

          datas = barray1[ind]
          meshPoint = mathutils.Vector()
          meshPoint.xyz = (datas[0,0],datas[1,0],datas[2,0])
          
          meshIndex : int = getIndex(mesh= mesh,point= meshPoint)

          rootbackPoint = mathutils.Vector()
          rootbackPoint.xyz = (datas[0,1],datas[1,1],datas[2,1]) 
          
          rootIndex :int = getIndex(mesh= backMesh,point= rootbackPoint)
          
          rootuv : mathutils.Vector = mathutils.Vector()
          if rootIndex != sys.maxsize:
            rootuv.xy = backobjMap[rootIndex].xy # backobjMap value is Vector

          point1 = mathutils.Vector() 
          point1.xyz = (datas[0,2],datas[1,2],datas[2,2])
        
          point1Index : int = getIndex(mesh= backMesh,point= point1)
          
          point1uv : mathutils.Vector = mathutils.Vector()
          if point1Index != sys.maxsize:
            point1uv.xy = backobjMap[point1Index].xy

          point2 = mathutils.Vector()
          point2.xyz = (datas[0,3],datas[1,3],datas[2,3])

          point2Index : int = getIndex(mesh= backMesh, point= point2)

          point2uv : mathutils.Vector = mathutils.Vector()
          if point2Index != sys.maxsize:
            point2uv.xy = backobjMap[point2Index].xy
            

          uv = [datas[0,4],datas[1,4]]
          
          #get three points uv
          #  
          puv : mathutils.Vector = mathutils.Vector()

          if (rootIndex != sys.maxsize and
              point1Index != sys.maxsize and
              point2Index != sys.maxsize 
              ):

              puv = base.TrigonoMetricParameterEquations(point0= rootuv,point1= point1uv, point2= point2uv,u= uv[0],v= uv[1]) 
          else:
             find = (rootIndex != sys.maxsize,point1Index != sys.maxsize,point2Index != sys.maxsize)
             raise RuntimeWarning("root:" + str(find[0]) + "\n" + "point1:" + str(find[1]) + "\n" + "point2:" + str(find[2])) 

          if meshIndex != sys.maxsize and puv.xyz != mathutils.Vector().xyz:

            obj_layer[meshMap[meshIndex]].uv.x = puv.x
            obj_layer[meshMap[meshIndex]].uv.y = puv.y
          else:
            raise RuntimeWarning("don't find this point in" + obj.name + "position :  " + str(meshPoint) + "\n" + "and don't find mapping points")

      lookMouse.unlookMouse()

      backMesh.free()
      mesh.free()
      


class UVTexture_OT_UvMappingInitDataOperator(bpy.types.Operator):

    bl_idname: str = 'object.uvmappinginitdata'
    bl_label: str = 'get all data to run uvmapping'

    
    uvMappingObjectName = bpy.props.StringProperty(name='uvMappingObjectName',default='None')

    backGroundObjName = bpy.props.StringProperty(name='backGroundObjName',default='None')

    def check(self,context) -> bool:
      ...

    def invoke(self, context, event):
       return super().invoke(context, event)

    def execute(self, context):

      updateDatas(context=context,
                  uvMappingObjectName= self.uvMappingObjectName,
                  backGroundObjName=self.backGroundObjName
                  )

      

   