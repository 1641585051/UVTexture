import enum

import bpy
import enum

from bpy.types import Struct


# control
class BlendMode(enum.Enum):
    '''BlendMode use PS ,don't use Contrast blend mode'''

    Normal = 'normal'
    '''正常'''

    Darken = 'darken'
    '''变暗'''

    Multiply = 'multiply'
    '''正片叠底'''

    ColorBurn = 'colorBurn'
    '''颜色加深'''

    Deep = 'deep'
    '''深色'''

    Lighten = 'lighten'
    '''变亮'''

    Screen = 'screen'
    '''滤色'''

    ColorDodge = 'colorDodge'
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

    LinearBurn = 'linearBurn'
    '''线性加深'''

    LinearDodge = 'linearDodge'
    '''线性加深'''

    Overlay = 'overlay'
    '''叠加'''

    HardLight = 'hardLight'
    '''强光'''

    SoftLight = 'softLight'
    '''柔光'''

    VividLight = 'vividLight'
    '''亮光'''

    LinearLight = 'linearLight'
    '''线性光'''

    PinLight = 'pinLight'
    '''点光'''

    HardMix = 'hardMix'
    '''实色混合'''



blend_id = str("BlendMode_")

modes = [
    
    (blend_id + str(BlendMode.Normal),str(BlendMode.Normal),str(BlendMode.Normal),'ALIGN_JUSTIFY',0),
    (blend_id + str(BlendMode.Darken),str(BlendMode.Darken),str(BlendMode.Darken),'ALIGN_JUSTIFY',1),
    (blend_id + str(BlendMode.Multiply),str(BlendMode.Multiply),str(BlendMode.Multiply),'ALIGN_JUSTIFY',2),
    (blend_id + str(BlendMode.ColorBurn),str(BlendMode.ColorBurn),str(BlendMode.ColorBurn),'ALIGN_JUSTIFY',3),
    (blend_id + str(BlendMode.Deep),str(BlendMode.Deep),str(BlendMode.Deep),'ALIGN_JUSTIFY',4),
    (blend_id + str(BlendMode.Lighten),str(BlendMode.Lighten),str(BlendMode.Lighten),'ALIGN_JUSTIFY',5),
    (blend_id + str(BlendMode.Screen),str(BlendMode.Screen),str(BlendMode.Screen),'ALIGN_JUSTIFY',6),
    (blend_id + str(BlendMode.ColorDodge),str(BlendMode.ColorDodge),str(BlendMode.ColorDodge),'ALIGN_JUSTIFY',7),
    (blend_id + str(BlendMode.Shallow),str(BlendMode.Shallow),str(BlendMode.Shallow),'ALIGN_JUSTIFY',8),
    (blend_id + str(BlendMode.Difference),str(BlendMode.Difference),str(BlendMode.Difference),'ALIGN_JUSTIFY',9),
    (blend_id + str(BlendMode.Hue),str(BlendMode.Hue),str(BlendMode.Hue),'ALIGN_JUSTIFY',10),
    (blend_id + str(BlendMode.Saturation),str(BlendMode.Saturation),str(BlendMode.Saturation),'ALIGN_JUSTIFY',11),
    (blend_id + str(BlendMode.Color),str(BlendMode.Color),str(BlendMode.Color),'ALIGN_JUSTIFY',12),
    (blend_id + str(BlendMode.Brightness),str(BlendMode.Brightness),str(BlendMode.Brightness),'ALIGN_JUSTIFY',13),
    (blend_id + str(BlendMode.LinearBurn),str(BlendMode.LinearBurn),str(BlendMode.LinearBurn),'ALIGN_JUSTIFY',14), 
    (blend_id + str(BlendMode.Overlay),str(BlendMode.Overlay),str(BlendMode.Overlay),'ALIGN_JUSTIFY',15),
    (blend_id + str(BlendMode.HardLight),str(BlendMode.HardLight),str(BlendMode.HardLight),'ALIGN_JUSTIFY',16),
    (blend_id + str(BlendMode.SoftLight),str(BlendMode.SoftLight),str(BlendMode.SoftLight),'ALIGN_JUSTIFY',17), 
    (blend_id + str(BlendMode.VividLight),str(BlendMode.VividLight),str(BlendMode.VividLight),'ALIGN_JUSTIFY',18),
    (blend_id + str(BlendMode.LinearLight),str(BlendMode.LinearLight),str(BlendMode.LinearLight),'ALIGN_JUSTIFY',19),
    (blend_id + str(BlendMode.HardMix),str(BlendMode.HardMix),str(BlendMode.HardMix),'ALIGN_JUSTIFY',20) 
  
 
]   

# control
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
    (blur_id + str(BlurType.Gaussian),str(BlurType.Gaussian),0),
    (blur_id + str(BlurType.Box),str(BlurType.Box),1),
    (blur_id + str(BlurType.Kawase),str(BlurType.Kawase),2),
    (blur_id + str(BlurType.Dual),str(BlurType.Dual),3),
    (blur_id + str(BlurType.Bokeh),str(BlurType.Bokeh),4),
    (blur_id + str(BlurType.TiltShift),str(BlurType.TiltShift),5),
    (blur_id + str(BlurType.Iris),str(BlurType.Iris),6),
    (blur_id + str(BlurType.Grainy),str(BlurType.Grainy),7),
    (blur_id + str(BlurType.Radial),str(BlurType.Radial),8),
    (blur_id + str(BlurType.Directional),str(BlurType.Directional),9)
    
]





#control
#Expend
class BakeTemplate(enum.Enum):
      '''expend  this will have other template
     
      '''
      Base = '0' # func : BakeNodeTreeTemplate.BakeNodeTreeTemplate0
   




template_id = str('template_')

bakeTemplates = [

   (template_id +str(BakeTemplate.Base),str(BakeTemplate.Base),str(BakeTemplate.Base),'MOD_CLOTH',0),



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
       
      
    ) 

    isUseAlphaTexture = bpy.props.BoolProperty(
       
       name="isUseAlphaTexture",
       description="using AlphaTexture is or not",
       default=False

    )


    bakeTemplateType = bpy.props.EnumProperty(

      items= bakeTemplates,
      name= "bakeTemplate",
      description= 'bake image template make node tree func',
      default= template_id + str(BakeTemplate.Base),
      update= lambda self,context: None



    )





#expend
class UVImage_stack_item(bpy.types.PropertyGroup):
    
    stackActive = bpy.props.BoolProperty(

      name= 'stackActive',
      description= 'stack_item_active',
      default= True

    )

    # a pool of parameters for all controls







