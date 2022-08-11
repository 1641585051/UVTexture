from this import d
import bpy
from bpy.types import Struct

from .UVListLayer import UVTextureLayer


defaultBakegroundObjName = "Null"


class UVTextureOutPutConfig(bpy.types.PropertyGroup):

    textureSideLength = bpy.props.IntProperty(

       name='textureSideLength',
       description= 'output texture side length',
       default= 1024,
       min= 512, 
       max= 10240


    )

    float32 = bpy.props.BoolProperty(

        name='isUseFloat32',
        description= "use 32-bit float image",
        default= False,

        )

    backgroundObjectName = bpy.props.StringProperty(

        name='backgroundObjectName',
        description="uvTexture base object (backgroung obj)",
        default=defaultBakegroundObjName,
        maxlen=128,
         

        )    



#expend
class BakeExtendTemplateData(bpy.types.PropertyGroup):
    '''this PropertyGroup need add attr if create new template func
    
       see BakeModeTreeTemplate.* in BakeModeTreeTemplate.py
       see need___Template0___list = ('...','...')

     '''


    color = bpy.props.FloatVectorProperty(

      name='color',
      description= 'bake color',
      default= (1.0,1.0,1.0),
      min= 0.0,
      max= 1.0

    )

    strengh = bpy.props.FloatProperty(
      
      name= 'strengh',
      description= 'bake strengh in Emisson',
      default= 1.0,
      min= 0.0,
      max= 2.0


    )
    
    #expend  
    #....





class UVBakeImageConfigData:

     widthData : int = 1024
     heightData : int = 1024
     colorData : tuple[float,float,float] = (0.0,0.0,0.0)
     isFloat32 : bool = False

     def __init__(self,width: int,height: int,color: tuple[float,float,float],isFloat32: bool):
         self.widthData = width
         self.heightData = height
         self.colorData = color
         self.isFloat32 = isFloat32


class UVBakeImageConfig(bpy.types.PropertyGroup):
     '''
       texture image use square style 
     
     width / height must is one''' 


     width = bpy.props.IntProperty(
        
        name='width',
        description= "image width",
        default=1024,
        min= 512,
        max= 10240,
        
        )

     height = bpy.props.IntProperty(
        
        name='height',
        description= "image width",
        default=1024,
        min= 512,
        max= 10240,
        
        )
     
     color = bpy.props.FloatVectorProperty(

        name='color',
        description= "image color",
        default=(0,0,0),
        min= 0.0,
        max= 1.0
        
        )

     float32 = bpy.props.BoolProperty(

        name='isUseFloat32',
        description= "use 32-bit float image",
        default= False,

        )



class UVTree_list_item(bpy.types.PropertyGroup):

    active = bpy.props.BoolProperty(

        name="active",
        description="layout is active?",
        default=True,

    )
    
    layerName = bpy.props.StringProperty(
        
        name="LayoutName",
        description="uv texture layout name",
        default= "Default",
        maxlen= 64,
        
    )

    uvTextureLayer = bpy.props.PointerProperty(

       type=UVTextureLayer,
       name="UVTextureLayer",
       description="layer type"

    )

    @classmethod
    def bl_rna_get_subclass(cls, id: str, default=None) -> Struct:
        return super().bl_rna_get_subclass(cls,id,default)


    @classmethod
    def bl_rna_get_subclass_py(cls, id: str, default=None):
        super().bl_rna_get_subclass_py(cls,id,default)

 

def UVTextureProperties():

    bpy.types.Scene.uv_texture_list = bpy.props.CollectionProperty(

        type=UVTree_list_item,
        name="uv_texture_list",
        description= "uv texture main data list"

    )


    bpy.types.Scene.uv_texture_list_index = bpy.props.IntProperty(
       
        name="uv_texture_list_index",
        default= 0,
        min= 0

        )

    bpy.types.Scene.uv_bake_image_config = bpy.props.CollectionProperty(

        type=UVBakeImageConfig,
        name="uv_bake_image_config",
        description= "uv_texture base config of bake image " 
      
        )


    bpy.types.Scene.bake_extend_template_data = bpy.props.CollectionProperty(

        type=BakeExtendTemplateData,
        name= "bake_extend_template_data",
        description= "bake base data collection"   


        )    


    bpy.types.Scene.uv_texture_output_config = bpy.props.CollectionProperty(

         type=UVTextureOutPutConfig,
         name= "uv_texture_output_config",
         description= "UVTexture output config" 
        

        )    