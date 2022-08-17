

import bpy


from . import UVListLayer

def update(self,func):
    for ind in range(UIListData.layerMaxNum):
      try:
         func(self,ind)
      except:
         break   

def activeUpdate(self,context):

   def func(self,ind :int):
      item = bpy.context.scene.uv_texture_list[ind]
      item.active = getattr(self,"active_" + str(ind))
      
   update(self= self,func= func)

def layerNameUpdate(self,context):

    def func(self,ind :int):
       item = bpy.context.scene.uv_texture_list[ind]
       item.layerName = getattr(self,'layerName_' + str(ind))

    update(self= self,func= func)


def coverObjNameUpdate(self,context):
    
    def func(self,ind :int):
       item = bpy.context.scene.uv_texture_settings[ind]
       item.coverObjName = getattr(self,'coverObjName_' + str(ind))

    update(self= self,func= func)

def blendModeUpdate(self,context):
     
    def func(self,ind :int):
      item = bpy.context.scene.uv_texture_settings[ind]
      item.blendMode = getattr(self,'blendMode_' + str(ind))

    update(self= self,func= func)

def isUseAlphaTextureUpdate(self,context):
    
    def func(self,ind :int):
      item = bpy.context.scene.uv_texture_settings[ind]
      item.isUseAlphaTexture = getattr(self,'isUseAlphaTexture_' + str(ind))

    update(self= self,func= func) 

def bakeTemplateTypeUpdate(self,context):
    
    def func(self,ind :int):
      item = bpy.context.scene.uv_texture_settings[ind]
      item.bakeTemplateType = getattr(self,'bakeTemplateType_' + str(ind))
    
    update(self= self,func= func)








#image stack 
def stackActiveUpdate(self,context):

    index = bpy.context.scene.layer_choose_index
    bpy.context.scene.image_stack_list[index].stackActive = getattr(self,'stackActive')


#------

class UIListData:

   layerMaxNum : int = 99
   layerMinNum : int = 1
    


   def init(self):
     
      listData : UIListData = bpy.types.Scene.uilistData
       
      for i in range(listData.layerMaxNum):
       #active (bool) to  uv_texture_list.active
         setattr(bpy.types.Scene,'active_' + str(i),bpy.props.BoolProperty(
                                               name='active_' + str(i),
                                               default=True,
                                               update= activeUpdate 
                                               ))  
       #layerName (string)  to  uv_texture_list.layerName
         setattr(bpy.types.Scene,'layerName_' + str(i),bpy.props.StringProperty(
                                               name='layerName_' + str(i),
                                               default="",
                                               update= layerNameUpdate
                                               ))
      #coberObjName (string) to  uv_texture_settings.coverObjName
         setattr(bpy.types.Scene,'coverObjName_' + str(i),bpy.props.StringProperty(
                                               name='coverObjName_' + str(i),  
                                               default="",
                                               update= coverObjNameUpdate
                                               )) 
       
         setattr(bpy.types.Scene,'blendMode_' + str(i),bpy.props.EnumProperty(
                                               items= UVListLayer.modes,
                                               name='blendMode_' + str(i),
                                               default= UVListLayer.blend_id + str(UVListLayer.BlendMode.Normal),
                                               update= blendModeUpdate
                                               ))

         setattr(bpy.types.Scene,'isUseAlphaTexture_' + str(i),bpy.props.BoolProperty(
                                               name= 'isUseAlphaTexture_' + str(i),
                                               default= True,
                                               update= isUseAlphaTextureUpdate
                                               )) 

         setattr(bpy.types.Scene,'bakeTemplateType_' + str(i),bpy.props.EnumProperty(
                                               items= UVListLayer.bakeTemplates,
                                               name= 'bakeTemplateType_' + str(i),
                                               default= UVListLayer.template_id + str(UVListLayer.BakeTemplate.Base),  
                                               update= bakeTemplateTypeUpdate
                                               )) 


      # image Stack
      setattr(bpy.types.Scene,'stackActive',bpy.props.BoolProperty(

                                               name= 'stackActive',
                                               default= True,
                                               update= stackActiveUpdate
                                               )) 
           



   def unload(self):

      listData : UIListData = bpy.types.Scene.uilistData
     
      for i in range(listData.layerMaxNum):
          
          delattr(bpy.types.Scene,'active_' + str(i))

          delattr(bpy.types.Scene,'layerName_' + str(i))
           
          delattr(bpy.types.Scene,'coverObjName_' + str(i)) 

          delattr(bpy.types.Scene,'blendMode_' + str(i))

          delattr(bpy.types.Scene,'isUseAlphaTexture_' + str(i))

          delattr(bpy.types.Scene,'bakeTemplateType_' + str(i))
