

import bpy
from ..dataDefine import DataProperty

from . import UVListLayer
from .gpuDataDifine import gpu_photo_stack
from ..UVOperators import UV_UI_Operators
from ..tools import gpuEnv


def textureSideLengthUpdate(self,context):
    
    index = getattr(self,'layer_choose_index')
    size = getattr(self,'textureSideLength')
    
    data = bpy.context.scene.uv_texture_output_config[index]
    data.textureSideLength = size

    item = bpy.context.scene.uv_bake_image_config[index]
    item.width = size
    item.height = size  

    # get globel image stacks 
    stacks = UV_UI_Operators.getImageStackDict()
    if gpuEnv.NVorAmd:

        stack : gpu_photo_stack.gpuImageStack = stacks[index]
        stack.ResetStackSize(width= size,height= size)

    else:
       pass


def float32Update(self,context):

    index = getattr(self,'layer_choose_index')
    float32 = getattr(self,'float32')
    
    data = bpy.context.scene.uv_texture_output_config[index]
    data.float32 = float32  

    item = bpy.context.scene.uv_bake_image_config[index]
    item.float32 = float32
 

def mappingSampleNumsUpdate(self,context):

    index = getattr(self,'layer_choose_index')
    mappingSampleNums = getattr(self,'mappingSampleNums')
    
    data = bpy.context.scene.uv_texture_output_config[index]
    data.mappingSampleNums = mappingSampleNums



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
    
    Istack = getattr(self,'Image_stack_list' + str(index))
    for i in len(Istack):
       Istack[i].stackActive = getattr(self,'stackActive')


def effectActive(self,context):

    index = bpy.context.scene.layer_choose_index
    istackIndex = bpy.context.scene.stack_choose_index
    Istack = getattr(self,'Image_stack_list' + str(index))
    Istack[istackIndex].effectActive = getattr(self,+ 'effectActive' +str(istackIndex))


def effectTypeUpdate(self,context):

    index = bpy.context.scene.layer_choose_index
    istackIndex = bpy.context.scene.stack_choose_index
    Istack = getattr(self,'Image_stack_list' + str(index))
    Istack[istackIndex].effectType = getattr(self,+ 'effectType' +str(istackIndex))





#------

class UIListData:

   layerMaxNum : int = 99
   layerMinNum : int = 1
    


   def init(self):
     
      listData : UIListData = bpy.types.Scene.uilistData
       
      setattr(bpy.types.Scene,'textureSideLength',bpy.props.IntProperty(
                                               name= 'textureSideLength',
                                               default=1024,
                                               min=512,
                                               max=10240,
                                               update= textureSideLengthUpdate
                                               ))  

      setattr(bpy.types.Scene,'float32',bpy.props.BoolProperty(
                                               name= 'float32',
                                               default= True,
                                               update= float32Update
 
                                               ))

      setattr(bpy.types.Scene,'mappingSampleNums',bpy.props.IntProperty(
                                               name= 'mappingSampleNums',
                                               default= 128,
                                               min=64,
                                               max=1024,
                                               update= mappingSampleNumsUpdate

                                               ))


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
                                               description= "this stack is used to handle the bake image",
                                               default= True,
                                               update= stackActiveUpdate
                                               )) 
           

      setattr(bpy.types.Scene,'stack_choose_index',bpy.props.IntProperty(
                                               name= 'stack_choose_index',
                                               default= -1,
                                               min= -1

                                               ))


      UVListLayer.regisiterItemAttrs()

      for i in range(listData.layerMaxNum):
        # this attr not show UI
        setattr(bpy.types.Scene,'Image_stack_list' + str(i),bpy.props.CollectionProperty(

                                               type= DataProperty.UVImage_stack_item,  
                                               name= 'Image_stack_list' + str(i),
                                               description=  'image stack item data struct'  

                                               ))
      
        # this attr not show UI   
        setattr(bpy.types.Scene,'Image_stack_index'+ str(i),bpy.props.IntProperty(

                                               name= 'Image_stack_index'+ str(i),
                                               default= -1,
                                               min= -1,
                                                 
                                               ))

        setattr(bpy.types.Scene,'effectActive'+ str(i),bpy.props.BoolProperty(

                                               name= 'effectActive'+ str(i),
                                               default= True,
                                               update= effectActive

                                               ))   
 
        setattr(bpy.types.Scene,'effectType' + str(i),bpy.props.EnumProperty(
                                               
                                               items= UVListLayer.alltypes,
                                               name= 'effectType' + str(i),
                                               default= UVListLayer.blur_id + str(UVListLayer.BlurType.Null),  
                                               update= effectTypeUpdate    

                                               ))

