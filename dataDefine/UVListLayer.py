import enum

import bpy
import enum

from bpy.types import Struct
from ..tools import tips

class BlendMode(enum.Enum):
    '''BlendMode use PS ,don't use Contrast blend mode'''

    Normal = 'normal'
    '''正常'''

    Dissolve = 'dissolve'
    '''溶解'''

    Darken = 'darken'
    '''变暗'''

    PositiveSheetStacked = 'positiveSheetStacked'
    '''正片叠底'''

    ColorDeepened = 'colorDeepened'
    '''颜色加深'''

    Deep = 'deep'
    '''深色'''

    Brighten = 'brighten'
    '''变亮'''

    ColorFilter = 'colorFilter'
    '''滤色'''

    ColorLightning = 'colorLightning'
    '''颜色减淡'''

    Shallow = 'shallow'
    '''浅色'''

    Difference = 'difference'
    '''差值'''

    Hue = 'hue'
    '''色相'''

    Saturation = 'saturation'
    '''饱和度'''

    Color = 'color'
    '''颜色'''

    Brightness = 'brightness'
    '''亮度'''

blend_id = str("BlendMode_")

modes = [
    (blend_id + str(BlendMode.Normal),str(BlendMode.Normal),str(BlendMode.Normal)),
    (blend_id + str(BlendMode.Dissolve),str(BlendMode.Dissolve),str(BlendMode.Dissolve)),
    (blend_id + str(BlendMode.Darken),str(BlendMode.Darken),str(BlendMode.Darken)),
    (blend_id + str(BlendMode.PositiveSheetStacked),str(BlendMode.PositiveSheetStacked),str(BlendMode.PositiveSheetStacked)),
    (blend_id + str(BlendMode.ColorDeepened),str(BlendMode.ColorDeepened),str(BlendMode.ColorDeepened)),
    (blend_id + str(BlendMode.Deep),str(BlendMode.Deep),str(BlendMode.Deep)),
    (blend_id + str(BlendMode.Brighten),str(BlendMode.Brighten),str(BlendMode.Brighten)),
    (blend_id + str(BlendMode.ColorFilter),str(BlendMode.ColorFilter),str(BlendMode.ColorFilter)),
    (blend_id + str(BlendMode.ColorLightning),str(BlendMode.ColorLightning),str(BlendMode.ColorLightning)),
    (blend_id + str(BlendMode.Shallow),str(BlendMode.Shallow),str(BlendMode.Shallow)),
    (blend_id + str(BlendMode.Difference),str(BlendMode.Difference),str(BlendMode.Difference)),
    (blend_id + str(BlendMode.Hue),str(BlendMode.Hue),str(BlendMode.Hue)),
    (blend_id + str(BlendMode.Saturation),str(BlendMode.Saturation),str(BlendMode.Saturation)),
    (blend_id + str(BlendMode.Color),str(BlendMode.Color),str(BlendMode.Color)),
    (blend_id + str(BlendMode.Brightness),str(BlendMode.Brightness),str(BlendMode.Brightness))

]   

class BlurType(enum.Enum):
    '''blur type :don't use Motion Blur'''


    Null = "null" 

    Gaussian = 'gaussian' 
    '''高斯模糊'''
    
    Box = 'box'
    '''方框模糊'''

    Kawase = 'kawase'
    '''Kawase模糊'''

    Dual = 'dual'
    '''双重模糊'''

    Bokeh = 'bokeh'
    '''散景模糊'''

    TiltShift = 'tiltShift'
    '''移轴模糊'''

    Iris = 'iris'
    '''光圈模糊'''

    Grainy = 'grainy'
    '''粒状模糊'''

    Radial = 'radial'
    '''径向模糊'''

    Directional = 'directional'
    '''方向模糊'''

blur_id = str("BlurType_")


blurTypes = [
    (blur_id + str(BlurType.Gaussian),str(BlurType.Gaussian),str(BlurType.Gaussian)),
    (blur_id + str(BlurType.Box),str(BlurType.Box),str(BlurType.Box)),
    (blur_id + str(BlurType.Kawase),str(BlurType.Kawase),str(BlurType.Kawase)),
    (blur_id + str(BlurType.Dual),str(BlurType.Dual),str(BlurType.Dual)),
    (blur_id + str(BlurType.Bokeh),str(BlurType.Bokeh),str(BlurType.Bokeh)),
    (blur_id + str(BlurType.TiltShift),str(BlurType.TiltShift),str(BlurType.TiltShift)),
    (blur_id + str(BlurType.Iris),str(BlurType.Iris),str(BlurType.Iris)),
    (blur_id + str(BlurType.Grainy),str(BlurType.Grainy),str(BlurType.Grainy)),
    (blur_id + str(BlurType.Radial),str(BlurType.Radial),str(BlurType.Radial)),
    (blur_id + str(BlurType.Directional),str(BlurType.Directional),str(BlurType.Directional))
    
]


#@tips.expend
class BakeTemplate(enum.Enum):
      '''expend  this will have other template
     
      '''
      Base = '0' # func : BakeNodeTreeTemplate.BakeNodeTreeTemplate0
   




template_id = str('template_')

bakeTemplates = [

   (template_id +str(BakeTemplate.Base),str(BakeTemplate.Base),str(BakeTemplate.Base)),



]






class UVTextureLayer(bpy.types.PropertyGroup):

    coverObjName = bpy.props.StringProperty(
       name="coverObjName",
       description="CoverObjName",
       default="Default",
       maxlen=128

    ) 
   
    
    blendMode = bpy.props.EnumProperty(
      
       items= modes,
       name="blendMode",
       description="uv_texture layer blendMode",
       default= blend_id + str(BlendMode.Normal),
       update= lambda self,context: None
      
    ) 

    isUseAlphaTexture = bpy.props.BoolProperty(
       
       name="isUseAlphaTexture",
       description="using AlphaTexture is or not",
       default=False

    )

    isUseBlur = bpy.props.BoolProperty(

       name="isUseBlur",
       description="using blur is or not",
       default=False


    )

    blurType = bpy.props.EnumProperty(

      items= blurTypes,
      name="blurType",
      description="uv_texture layer blurType",
      default= blur_id + str(BlurType.Null),
      update= lambda self,context: None
      
    )

    bakeTemplateType = bpy.props.EnumProperty(

      items= bakeTemplates,
      name= "bakeTemplate",
      description= 'bake image template make node tree func',
      default= template_id + str(BakeTemplate.Base),
      update= lambda self,context: None



    )


    @classmethod
    def bl_rna_get_subclass(cls, id: str, default=None) -> Struct:
        return super().bl_rna_get_subclass(cls,id,default)


    @classmethod
    def bl_rna_get_subclass_py(cls, id: str, default=None):
        super().bl_rna_get_subclass_py(cls,id,default)
