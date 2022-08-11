from typing import Any
import bpy

from ..dataDefine import DataProperty
from . import BakeNodeTreeTemplate




class UVTexture_OT_ObjectUVMapping(bpy.types.Operator):
   
   
   bl_idname :str = "object.uvmapping"
   bl_label: str = "mapping uv on target object"

   def check(self,context) -> bool:
      ...

   def invoke(self, context, event):
      return super().invoke(context, event)

   def execute(self, context):
      ...

   



class UVTexture_OT_UVLayerBakeUseTemplate0Operator(bpy.types.Operator):
   '''bake uv layer in Uv layer tree
      this Operator use Bake Template0 (BakeNodeTreeTemplate.BakeNodeTreeTemplate0 func)
      and only use GPU
   '''
   
   bl_idname :str = "object.UVLayerBake"
   bl_label: str = "bake uv layer"

   bakeImageName = bpy.props.StringProperty(name='bakeImageName',default='Render Result')
   '''bakeImageName is LayerName '''
   bakeObjectName = bpy.props.StringProperty(name='bakeObjectName',default='none')
   

   def check(self,context) -> bool:

       return (bpy.context.scene.render.engine == 'CYCLES' and
               bpy.context.scene.cycles.device == 'GPU'
              
              )

   def invoke(self, context, event):
      return super().invoke(context, event)

   def execute(self, context):

      #get datas
      index = 0
      imageConfig : DataProperty.UVBakeImageConfigData = None
      values = bpy.types.Scene.uv_texture_list.values()
      layerNames = list((value.layerName for value in values))
      if self.bakeImageName in layerNames :
         index = layerNames.index(self.bakeImageName)
      
         config = bpy.types.Scene.uv_bake_image_config[index]
      
         imageConfig = DataProperty.UVBakeImageConfigData(
                    width= config.width,
                    height= config.height,
                    color= config.color,
                    isFloat32= config.isFloat32 
                    )

      
         bpy.context.active_object = context.scene.objects[context.scene.objects.find(self.bakeObjectName)]

         obj = bpy.context.active_object

         image : bpy.types.Image = None  

         if self.bakeImageName not in (ima.name for ima in bpy.data.images.values()):
               image = bpy.data.images.new(
                       name= self.bakeImageName,
                       width= imageConfig.widthData,
                       height= imageConfig.heightData,
                       alpha= False,
                       float_buffer= imageConfig.isFloat32

                   )
         else:
               image = bpy.data.images[self.bakeImageName]

         templateType :str = values[index].bakeTemplateType

         func = BakeNodeTreeTemplate.findTemplateFunc(bl_enum= templateType) 
         func(object= obj,image= image,propertyData= bpy.types.Scene.bake_extend_template_data,
                                                      dataIndex=index
                                                       )

         bpy.context.view_layer.objects.active = obj
         bpy.ops.object.bake(type='EMIT',target='IMAGE_TEXTURES', save_mode='INTERNAL')

      
      else:
         raise Exception("bakeImageName is not LayerName")
         

   
      
   


         
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

