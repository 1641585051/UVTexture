from this import d, s
import bpy
import bmesh
from taichi.lang.matrix import Vector




from ..mars import tensor as ten 

from .. import numpy as np


## this file not have UVMapping Base Operator ,only have Calculation operators
## base operator in UV_operators.UVTexture_OT_ObjectUVMapping ...

gl_back_data : ten.Tensor = None
'''gl_back_data only valid in one operation'''

gl_mesh_data : ten.Tensor = None
'''gl_mesh_data only valid in one operation'''



class UVTExture_OT_UvMappingCalculateProjectionValue(bpy.types.Operator):

    bl_idname: str = 'object.calculateProjectionValue'  
    bl_label: str = 'get mapping project mesh data'

  
    def check(self,context) -> bool:
      ...

    def invoke(self, context, event):
       return super().invoke(context, event)

    def execute(self, context):

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


     

      from .. import taichi as ti
      from .. taichi import types
      
      ti.init(arch=ti.gpu)  

      
      spArr : np.ndarray = np.array(object= np.split(ary= datanpArr,indices_or_sections= 3,axis=1),dtype=np.float32)
      #  shape (3,4,n)

      materix : ti.Matrix = ti.Matrix.field(n= 3,m=4,dtype= ti.float32,shape=(n,1))
      # [  [[00,10,20,    [[00,10,20,
      #      01,11,21,      01,11,21,
      #      02,12,22,      02,12,22, .....
      #      03,13,23]],    03,13,23]],          ]

      temNDa : ti.MatrixNdarray = ti.MatrixNdarray(n=3 ,m= 4,dtype=ti.f32,shape=(n,1))
      temNDa.from_numpy(arr=spArr)
      
      @ti.kernel
      def fullMaterix():
        for ind in ti.grouped(materix):
           
           materix[ind] = temNDa[ind[0],0]
           # materix (3,4)(n,1) so grouped -> ind = [0,0]/[1,0]/ ... [n,0]
           # ind[0] = 0/1/...n

      fullMaterix()

      @ti.kernel
      def NormalRayCapture():
          for ind in ti.grouped(materix):

              data = materix[ind]
              mesh_point = ti.Vector([materix[ind][0,0],materix[ind][1,0],materix[ind][2,0]])
              back_point0 = ti.Vector([materix[ind][0,1],materix[ind][1,1],materix[ind][2,1]])
              back_point1 = ti.Vector([materix[ind][0,2],materix[ind][1,2],materix[ind][2,2]])
              back_point3 = ti.Vector([materix[ind][0,3],materix[ind][1,3],materix[ind][2,3]])
                  
              

        

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

      global gl_back_data
      gl_back_data = None

      global gl_mesh_data 
      gl_mesh_data = None 

      obj = context.scene.objects[context.scene.objects.find(self.uvMappingObjectName)]      

      backgroundObj = context.scene.objects[context.scene.objects.find(self.backGroundObjName)]  

      mesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(obj.to_mesh()) 

      objVerts : list[tuple[np.float32,np.float32,np.float32]] = list()
      objcount = mesh.verts.count()
      for i in range(objcount):
            ve = mesh.verts[i].co
            objVerts.append((ve.x,ve.y,ve.z))


      objarr = np.array(object= objVerts,dtype= np.float32).reshape()
      # ndarray shape (objcount,3)
      
      backMesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(backgroundObj.to_mesh()) 
      
      backVerts : list[tuple[np.float32,np.float32,np.float32]] = list()
      backcount = backMesh.verts.count()
      for i in range(backcount):
           ve = backMesh.verts[i].co
           backVerts.append((ve.x,ve.y,ve.z))

      backarr = np.array(object= backVerts,dtype= np.float32)
      # ndarray shape (backcount,3)

      global gl_back_data

      gl_back_data = ten.tensor(data= objarr,gpu= True)
      gl_back_data.execute()

      global gl_mesh_data

      gl_mesh_data = ten.tensor(data= backarr,gpu= True)
      gl_mesh_data.execute()


      mesh.free()

      

   