from distutils import core
import os
from unicodedata import name
import bpy
import bmesh
import sys
import mathutils

import numpy as np
import cv2

from ..dataDefine import DataProperty
from . import BakeNodeTreeTemplate,UV_UI_Operators

from ..UVMapping import base,UVMappingOperator

from ..tools import gpuEnv
from ..dataDefine.gpuDataDifine import gpu_photo_stack


class UVTexture_OT_Image_Stack_Compute(bpy.types.Operator):
    '''All the image algorithms are concentrated here
    
       All processing layers are calculated sequentially and
       the results are stored on image stack
    '''

    bl_idname :str = "object.stackcompute"
    bl_label: str = "Performs processing operations on the image"

    
    def check(self,context) -> bool:
      ...

   
    def execute(self, context):

      #self.report({'INFO'}) 
      

      return {'FINISHED'}


class UVTexture_OT_ObjectUVMapping(bpy.types.Operator):
   ''' need run UVTExture_OT_UvMappingCalculateProjectionValue
       to get mapping result
   '''
   
   bl_idname :str = "object.uvmapping"
   bl_label: str = "mapping uv on target object"

   def check(self,context) -> bool:
      ...

   
   def execute(self, context):
      
      resultDatas = UVMappingOperator.getResult()
      
      backgroundObj = context.scene.objects[context.scene.objects.find(self.backGroundObjName)]  

      backobjMap = base.makeUVVertMap(obj= backgroundObj,isContainsUVData= True)

      obj = context.scene.objects[context.scene.objects.find(self.uvMappingObjectName)]      
      
      meshMap,obj_layer = base.makeUVVertMap(obj= obj,isContainsUVData= False) 
      
      mesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(obj.to_mesh()) 
      
      backMesh : bmesh.types.BMesh = bmesh.types.BMesh.from_mesh(backgroundObj.to_mesh())

      def getIndex(mesh : bmesh.types.BMesh, point: mathutils.Vector):
        meshIndex : int = sys.maxsize
        for vert in mesh.verts:
             bvert : bmesh.types.BMVert = vert
             if bvert.co == point:
                 meshIndex = bvert.index
        return meshIndex

      bpy.context.active_object = obj
      
      for ind in range(resultDatas.shape[0]):

          datas = resultDatas[ind]
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
            self.report({'WARRING'},"don't find this point in" + obj.name + "position :  " + str(meshPoint) + "\n" + "and don't find mapping points")
            raise RuntimeWarning("don't find this point in" + obj.name + "position :  " + str(meshPoint) + "\n" + "and don't find mapping points")

      backMesh.free()
      mesh.free()
      

   



class UVTexture_OT_UVLayerBakeUseTemplateOperator(bpy.types.Operator):
   '''bake uv layer in Uv layer tree
      this Operator use Bake Template0 (BakeNodeTreeTemplate.BakeNodeTreeTemplate0 func)
      and only use GPU
   '''
   bl_options = 'BLOCKING'

   bl_idname :str = "object.uvlayerbake"
   bl_label: str = "bake uv layer"


   def check(self,context) -> bool:

       return (bpy.context.scene.render.engine == 'CYCLES' and
               bpy.context.scene.cycles.device == 'GPU'
              
              )

   def invoke(self, context, event):
      return super().invoke(context, event)

   def execute(self, context):

      
         scene = bpy.context.scene
         index = scene.layer_choose_index
         bakeImageName = scene.uv_texture_list[index].layerName

         #get datas
         imageConfig : DataProperty.UVBakeImageConfigData = None

         bakeObjectName = scene.uv_texture_settings[index].bakeObjName
      
         config = bpy.types.Scene.uv_bake_image_config[index]
      
         imageConfig = DataProperty.UVBakeImageConfigData(
                    width= config.width,
                    height= config.height,
                    color= config.color,
                    isFloat32= config.isFloat32 
                    )

      
         bpy.context.active_object = context.scene.objects[context.scene.objects.find(bakeObjectName)]

         obj = bpy.context.active_object

         image : bpy.types.Image = None  

         if bakeImageName not in (ima.name for ima in bpy.data.images.values()):
               image = bpy.data.images.new(
                       name= bakeImageName,
                       width= imageConfig.widthData,
                       height= imageConfig.heightData,
                       alpha= False,
                       float_buffer= imageConfig.isFloat32

                   )
               image.generated_color = list(imageConfig.colorData)

         else:
               image = bpy.data.images[bakeImageName]

         templateType :str = scene.uv_texture_settings[index].bakeTemplateType

         func = BakeNodeTreeTemplate.findTemplateFunc(bl_enum= templateType) 
         func(object= obj,image= image,propertyData= bpy.types.Scene.bake_extend_template_data,
                                                      dataIndex=index
                                                       )

         bpy.context.view_layer.objects.active = obj
         
         bpy.ops.object.bake(type='EMIT',target='IMAGE_TEXTURES', save_mode='INTERNAL')
         # bake may be use thread ,if not The following code will work
         
         # Save the photo to the gpu_image_stack
         stackDict =  UV_UI_Operators.getImageStackDict()

         if gpuEnv.NVorAmd:
            stack : gpu_photo_stack.gpuImageStack = stackDict[scene.layer_choose_index]
            
            path = os.path.dirname(__file__) + os.sep + 'temp_' + image.name + '.jpg'

            image.save_render(filepath= path ,scene= scene)

            saveImage = cv2.imread(filename= path)

            saveImage : np.ndarray = np.asarray(object= saveImage[:,:,:],dtype= np.float32)

            if saveImage.shape[2] == 3:
                alpha = np.full(shape= (saveImage.shape[0],saveImage.shape[1]),fill_value= 255.0,dtype= np.float32)
                saveImage = np.hstack((saveImage,alpha))

            stack.SetBakeImage(image= saveImage,index= index,backgroundColor= imageConfig.colorData)

            os.remove(path= path)

         else:

            pass

      
         return {'FINISHED'}


class UVTexture_OT_InitOperator(bpy.types.Operator):
   bl_idname :str = "object.inituvtexture"
   bl_label :str = "init UV_Texture"
   
   def check(self,context) -> bool:
      pass
   
   def invoke(self, context, event):
      return super().invoke(context, event)

   def execute(self, context):
 
      DefaultConfig = bpy.context.scene.uv_bake_image_config.add()
      DefaultConfig.width = 1024
      DefaultConfig.height = 1024
      DefaultConfig.color = (0.0,0.0,0.0)
      DefaultConfig.float32 = False

      


   
      return {'FINISHED'}


class UVTexture_OT_RunUVTextureOperator(bpy.types.Operator):
   '''UV_Texture main Operator '''

   bl_idname :str = "object.runuvtexture"
   bl_label :str = "Run UV_Texture"
   
   
   def check(self,context) -> bool:
       return ( bpy.context.scene.render.engine == 'CYCLES' and
                bpy.context.scene.cycles.device == 'GPU'
              
              )



   def invoke(self, context, event):
      return super().invoke(context, event)

   def execute(self, context):

      





   
      return {'FINISHED'}

