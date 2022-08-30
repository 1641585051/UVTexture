
import inspect
import os
from typing import Any

import bpy
import bmesh
import sys
import mathutils
import operator


import numpy as np
import cv2
import mars.tensor as ten


from ..dataDefine import DataProperty,ControlAlgorithms
from . import BakeNodeTreeTemplate,UV_UI_Operators

from ..UVMapping import base,UVMappingOperator

from ..tools import gpuEnv
from ..dataDefine.gpuDataDifine import gpu_photo_stack


class UVTexture_OT_Compute_All_Image_effect(bpy.types.Operator):
     '''compute all effects in all layer'''

     bl_idname :str = "object.computeallimageeffect"
     bl_label: str = "compute all image effect"

     bl_options = {'BLOCKING'}

     def check(self, context) -> bool:
        
        scene = bpy.context.scene

        return scene.finished_baking


     def execute(self, context):
        
        scene = bpy.context.scene
        scene.layer_choose_index = 0

        for lind in range(scene.uv_texture_list_index):
        
            scene.layer_choose_index = lind

            scene.stack_choose_index = 0
            
            stack_index = getattr(scene,'Image_stack_index'+ str(scene.layer_choose_index))

            for ind in range(stack_index):

               scene.stack_choose_index = ind

               bpy.ops.object.stackcompute('INVOKE_DEFAULT')
         
           
        return {'FINISHED'}


     



class UVTexture_OT_Image_Stack_Compute(bpy.types.Operator):
    '''All the image algorithms are concentrated here
    
       All processing layers are calculated sequentially and
       the results are stored on image stack
    '''

    bl_idname :str = "object.stackcompute"
    bl_label: str = "Performs processing operations on the image"


    def execute(self, context):

      funcs = ControlAlgorithms.all_effect_funcs
      
      scene = bpy.context.scene

      ind = scene.layer_choose_index

      imageStack = getattr(scene,'Image_stack_list' + str(ind))

      item = imageStack[scene.stack_choose_index]

      effectType = item.effectType     
      prameters : dict[str,Any] = {}
      
      for key in funcs:

         if operator.contains(effectType,key):
             
             imagestackStruct = None

             if gpuEnv.NVorAmd:
                 
                  imagestackStruct : gpu_photo_stack.gpuImageStack = UV_UI_Operators.getImageStackDict()[scene.layer_choose_index]
                
                  func = funcs[key]
                  spec = inspect.getfullargspec(func= func)
                  
                  for permeter in spec.args:

                     if permeter == 'a': # a is func peremeter 

                        prameters['a'] = imagestackStruct.GetBakeImage()

                     prameters[permeter] = getattr(item,permeter)

                  re = func(*(list(prameters.values()))) 

                  keys = list(imagestackStruct.__stacks.keys())

                  if effectType not in keys:
                     
                     imagedef = gpu_photo_stack.gpuImageDef(image_width= imagestackStruct.__width,image_height= imagestackStruct.__height,is64Bit= (imagestackStruct.__type == np.float64))
                     imagedef.gpuImage = re
                     imagestackStruct.add(effectType,imagedef)
                   
                  elif keys.index(effectType) == len(keys) - 1:

                     last = imagestackStruct.getlastData()
                     last.gpuImage = re
           
                  elif keys.index(effectType) != len(keys) - 1:

                     imagestackStruct.removeAssociateData(effectType) 
                     imagedef = gpu_photo_stack.gpuImageDef(image_width= imagestackStruct.__width,image_height= imagestackStruct.__height,is64Bit= (imagestackStruct.__type == np.float64))
                     imagedef.gpuImage = re
                     imagestackStruct.add(effectType,imagedef)
                      
                     imagestackStruct.RecalculateAllData(imagestackStruct.GetBakeImage(),ind) 
    
             else:
                pass 



      return {'FINISHED'}




class UVTexture_OT_MappingAllLayers(bpy.types.Operator):
   '''mapping all layers'''
   bl_idname :str = "object.mappingalllayers"
   bl_label: str = "mapping all layers"

   bl_option = {'BLOCKING'}

   def check(self, context) -> bool:
      
      scene = bpy.context.scene
      
      return scene.finished_mapping == False
  

   def execute(self, context):

      scene = bpy.context.scene
      scene.layer_choose_index = 0

      mappingsuccess = True

      for ind in range(scene.uv_texture_list_index):

         # list 0 is base obj position,should set base obj in zero element,and don't set coverObjName  
         if ind != 0:

            scene.layer_choose_index = ind
            
            try:
               
                  bpy.ops.object.calculateprojectionvalue('INVOKE_DEFAULT')

                  bpy.ops.object.uvmapping('INVOKE_DEFAULT')

            except RuntimeError as err:
                  mappingsuccess = False
                  self.report({'ERROR'},'failed mapping: --- {0}'.format(str(err)))
                  print('failed mapping: ---',err)

      scene.finished_mapping = mappingsuccess

      return {'FINISHED'}
   


class UVTexture_OT_ObjectUVMapping(bpy.types.Operator):
   ''' need run UVTExture_OT_UvMappingCalculateProjectionValue
       to get mapping result
   '''
   
   bl_idname :str = "object.uvmapping"
   bl_label: str = "mapping uv on target object"

   
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
             raise RuntimeError("root:" + str(find[0]) + "\n" + "point1:" + str(find[1]) + "\n" + "point2:" + str(find[2])) 

          if meshIndex != sys.maxsize and puv.xyz != mathutils.Vector().xyz:

            obj_layer[meshMap[meshIndex]].uv.x = puv.x
            obj_layer[meshMap[meshIndex]].uv.y = puv.y

          else:
            self.report({'WARRING'},"don't find this point in" + obj.name + "position :  " + str(meshPoint) + "\n" + "and don't find mapping points")
            raise RuntimeError("don't find this point in" + obj.name + "position :  " + str(meshPoint) + "\n" + "and don't find mapping points")

      backMesh.free()
      mesh.free()
      
      return {'FINISHED'}



class UVTexture_OT_ReBakeAllLayers(bpy.types.Operator):
      '''bake all layers, and put bake image in image stack'''

      bl_idname :str = "object.bakealllayers"
      bl_label: str = "bake all layers"

      bl_options = {'BLOCKING'}

      def check(self, context) -> bool:
         
         scene = bpy.context.scene
         
         return scene.finished_mapping 

      def execute(self, context):

         try:

            if scene.uv_texture_list_index != -1:

               # in blender bake only support cycles engine
               bpy.context.scene.render.engine = 'CYCLES'
               # open GPU compute
               bpy.context.scene.cycles.device = 'GPU'

               scene = bpy.context.scene
               scene.layer_choose_index = 0

               for ind in range(scene.uv_texture_list_index): 

                  scene.layer_choose_index = ind

                  bpy.ops.object.uvlayerbake('INVOKE_DEFAULT')


         except Exception as e:
              print('exception > {0}'.format(str(e)))

         else:

           scene.finished_mapping = False
           scene.finished_baking = True

         return {'FINISHED'}



class UVTexture_OT_UVLayerBakeUseTemplateOperator(bpy.types.Operator):
   '''bake uv layer in Uv layer tree
      this Operator use Bake Template0 (BakeNodeTreeTemplate.BakeNodeTreeTemplate0 func)
      and only use GPU
   '''
   
   bl_idname :str = "object.uvlayerbake"
   bl_label: str = "bake uv layer"

   #bl_options = {'BLOCKING'}

   def check(self,context) -> bool:

       return (bpy.context.scene.render.engine == 'CYCLES' and
               bpy.context.scene.cycles.device == 'GPU'
              
              )

   

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
         
         bpy.ops.object.bake(type='EMIT',target='IMAGE_TEXTURES', save_mode='EXTERNAL')
         # bake may be use thread ,if not The following code will work
         
         # Save the photo to the gpu_image_stack
         stackDict =  UV_UI_Operators.getImageStackDict()

         path = os.path.dirname(__file__) + os.sep + 'temp_' + image.name + '.jpg'

         image.save_render(filepath= path ,scene= scene)
         
         saveImage = cv2.imread(filename= path)

         saveImage : np.ndarray = np.asarray(object= saveImage[:,:,:],dtype= np.float32)

         if gpuEnv.NVorAmd:

            stack : gpu_photo_stack.gpuImageStack = stackDict[scene.layer_choose_index]
            
            if saveImage.shape[2] == 3:
                alpha = np.full(shape= (saveImage.shape[0],saveImage.shape[1]),fill_value= 255.0,dtype= np.float32)
                saveImage = np.hstack((saveImage,alpha))

            stack.SetBakeImage(image= saveImage,index= index,backgroundColor= imageConfig.colorData)

         else:

            pass
         
         os.remove(path= path)


         return {'FINISHED'}


class UVTexture_OT_InitOperator(bpy.types.Operator):
   bl_idname :str = "object.inituvtexture"
   bl_label :str = "init UV_Texture"
   
   def check(self,context) -> bool:
      
      return True
  

   def execute(self, context):
 
    

      
      return {'FINISHED'}


def SynthesizeFinalResult(a : Any,uvlistsettings):
    '''
       a : image data, 
       list : uv_texture_list
       
    '''
    # check loop before two obj covered
    def DecideLoopCoverage(ind) -> tuple[bool,str]:


      ...

    bakeObjs : list[Any] = list((item.bakeObjName for item in uvlistsettings)) 

    for ind in range(len(uvlistsettings)):
            
         en = DecideLoopCoverage(ind)
            
         if(en[0]):

            if ind != 0:
               covername = uvlistsettings[ind].coverObjName
               for element in bakeObjs:
                  if isinstance(element,str) and covername == element:
                     trueind = bakeObjs.index(element)
                     tem : list[Any] = [bakeObjs[trueind]]
                     tem.append(uvlistsettings[ind].bakeObjName)
                     bakeObjs[trueind] = tem
                     
                  elif isinstance(element,list[Any]):
                     if element[0] == covername:
                        element[0].append(uvlistsettings[ind].bakeObjName)
                        
            else:

               raise RuntimeError('Error : ---' + uvlistsettings[ind].bakeObjName +' and ' + en[1] + 'generate loops')



    if gpuEnv.NVorAmd:

       baseImage : ten.Tensor = a

      

    else:

      pass   

    ...



class UVTexture_OT_RunUVTextureOperator(bpy.types.Operator):
   '''UV_Texture main Operator ,when we has all data we need, run this'''

   bl_idname :str = "object.runuvtexture"
   bl_label :str = "Run UV_Texture"
   
   
   def check(self,context) -> bool:

       return True



   def execute(self, context):

      scene = bpy.context.scene
      uvlistsettings = scene.uv_texture_settings
      config = scene.uv_texture_output_config
      size = config.textureSideLength

      strackDict = UV_UI_Operators.getImageStackDict()
         
      re = None   

      if gpuEnv.NVorAmd:

         
         re = ten.full(shape= (size,size,4),fill_value= 0.0,dtype= np.float32,gpu= True)

         basestack : gpu_photo_stack.gpuImageStack = strackDict[0] # 0 elemant is base obj

         ten.add(x1= re,x2= basestack.GetBakeImage(),out= re).execute() 


      else:
         pass



      re = SynthesizeFinalResult(re,uvlistsettings)

   
      return {'FINISHED'}

