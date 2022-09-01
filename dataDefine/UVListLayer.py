import enum
from typing import Any

import bpy
import enum




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

    Exclusion = 'exclusion'
    '''排除'''

    Subtract = 'subtract'
    '''减去'''

    Divide = 'divide'
    '''划分'''

    # alpha blend

    AlphaBlend = 'alphablend'
    '''
       alpha blend use Unity base alpha mode \n
       endColor = (srcColor * srcFactor) + (dstColor * dstFactor),\n
       srcColor is downColor and dstColor mains upcolor\n
       
       Factor less than Unity : One ,Zero ,SrcAlpha, DstAlpha, OneMinusSrcAlpha, OneMinusDstAlpha,\n
       don't use Color value Factor \n
       
       blendOp don't has Unity base Op (Add ,Sub ,Min ,Max ,RevSub), it use Other Blend Mode replace then\n
        
       alphaBlend don't have an explicit type on UI
       if layer isUseAlphaTexture is True , UVTexture will use the provided alpha texture for calculation\n

       

    '''




blend_id = str("BlendMode_")

modes = [

    (blend_id + str(BlendMode.Normal),str(BlendMode.Normal),str(BlendMode.Normal),'ALIGN_JUSTIFY',0),
    (blend_id + str(BlendMode.Darken),str(BlendMode.Darken),str(BlendMode.Darken),'ALIGN_JUSTIFY',1),
    (blend_id + str(BlendMode.Multiply),str(BlendMode.Multiply),str(BlendMode.Multiply),'ALIGN_JUSTIFY',2),
    (blend_id + str(BlendMode.ColorBurn),str(BlendMode.ColorBurn),str(BlendMode.ColorBurn),'ALIGN_JUSTIFY',3),
    #(blend_id + str(BlendMode.Deep),str(BlendMode.Deep),str(BlendMode.Deep),'ALIGN_JUSTIFY',*),
    (blend_id + str(BlendMode.Lighten),str(BlendMode.Lighten),str(BlendMode.Lighten),'ALIGN_JUSTIFY',4),
    (blend_id + str(BlendMode.Screen),str(BlendMode.Screen),str(BlendMode.Screen),'ALIGN_JUSTIFY',5),
    (blend_id + str(BlendMode.ColorDodge),str(BlendMode.ColorDodge),str(BlendMode.ColorDodge),'ALIGN_JUSTIFY',6),
    #(blend_id + str(BlendMode.Shallow),str(BlendMode.Shallow),str(BlendMode.Shallow),'ALIGN_JUSTIFY',*),
    (blend_id + str(BlendMode.Difference),str(BlendMode.Difference),str(BlendMode.Difference),'ALIGN_JUSTIFY',7),
    #(blend_id + str(BlendMode.Hue),str(BlendMode.Hue),str(BlendMode.Hue),'ALIGN_JUSTIFY',*),
    #(blend_id + str(BlendMode.Saturation),str(BlendMode.Saturation),str(BlendMode.Saturation),'ALIGN_JUSTIFY',*),
    #(blend_id + str(BlendMode.Color),str(BlendMode.Color),str(BlendMode.Color),'ALIGN_JUSTIFY',*),
    #(blend_id + str(BlendMode.Brightness),str(BlendMode.Brightness),str(BlendMode.Brightness),'ALIGN_JUSTIFY',*),
    (blend_id + str(BlendMode.LinearDodge),str(BlendMode.LinearDodge),str(BlendMode.LinearDodge),'ALIGN_JUSTIFY',8), 
    (blend_id + str(BlendMode.LinearBurn),str(BlendMode.LinearBurn),str(BlendMode.LinearBurn),'ALIGN_JUSTIFY',9), 
    (blend_id + str(BlendMode.Overlay),str(BlendMode.Overlay),str(BlendMode.Overlay),'ALIGN_JUSTIFY',10),
    (blend_id + str(BlendMode.HardLight),str(BlendMode.HardLight),str(BlendMode.HardLight),'ALIGN_JUSTIFY',11),
    (blend_id + str(BlendMode.SoftLight),str(BlendMode.SoftLight),str(BlendMode.SoftLight),'ALIGN_JUSTIFY',12), 
    (blend_id + str(BlendMode.VividLight),str(BlendMode.VividLight),str(BlendMode.VividLight),'ALIGN_JUSTIFY',13),
    (blend_id + str(BlendMode.LinearLight),str(BlendMode.LinearLight),str(BlendMode.LinearLight),'ALIGN_JUSTIFY',14),
    (blend_id + str(BlendMode.PinLight),str(BlendMode.PinLight),str(BlendMode.PinLight),'ALIGN_JUSTIFY',15),
    (blend_id + str(BlendMode.HardMix),str(BlendMode.HardMix),str(BlendMode.HardMix),'ALIGN_JUSTIFY',16),
    (blend_id + str(BlendMode.Exclusion),str(BlendMode.Exclusion),str(BlendMode.Exclusion),'ALIGN_JUSTIFY',17), 
    (blend_id + str(BlendMode.Subtract),str(BlendMode.Subtract),str(BlendMode.Subtract),'ALIGN_JUSTIFY',18), 
    (blend_id + str(BlendMode.Divide),str(BlendMode.Divide),str(BlendMode.Divide),'ALIGN_JUSTIFY',19), 
    
    # Deep,Shallow,Hue,Saturation,Color,Brightness
    # these are not intended to be achieved
    # there are two reasons for this 
    # 1). Deep and Shallow requires merging the channels of the picture,
    # which is not in line with our GPU computing philosophy
    # 2). Hue,Saturation,Color and Brightness uses the HSB color space,
    # whitch is not compatible with the wider RGB color space we expect to
    # use ,and to avoid conversion, does not use the HSB-related algorithm 
    # from Photoshop 

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
    (blur_id + str(BlurType.Null),str(BlurType.Null),str(BlurType.Null),str('ALIGN_JUSTIFY')),
    (blur_id + str(BlurType.Gaussian),str(BlurType.Gaussian),str(BlurType.Gaussian),str('ALIGN_JUSTIFY')),
    (blur_id + str(BlurType.Box),str(BlurType.Box),str(BlurType.Box),str('ALIGN_JUSTIFY')),
    #(blur_id + str(BlurType.Kawase),str(BlurType.Kawase),2),
    #(blur_id + str(BlurType.Dual),str(BlurType.Dual),3),
    #(blur_id + str(BlurType.Bokeh),str(BlurType.Bokeh),4),
    #(blur_id + str(BlurType.TiltShift),str(BlurType.TiltShift),5),
    #(blur_id + str(BlurType.Iris),str(BlurType.Iris),6),
    #(blur_id + str(BlurType.Grainy),str(BlurType.Grainy),7),
    #(blur_id + str(BlurType.Radial),str(BlurType.Radial),8),
    #(blur_id + str(BlurType.Directional),str(BlurType.Directional),9)
    
    # There are many fuzzy algorithms that do not have a good implementation,
    # so they are not displayed,and secondly,due to insufficient personalability,
    # for the time being only the Gaussion and box are available for
    # the time being 
 



]




#Expend
class Stroke(enum.Enum):

     Base = 'base'



strock_id = str('Strock_')


strocks = [

    (strock_id + str(Stroke.Base),str(Stroke.Base),str(Stroke.Base),str('META_PLANE')),




]


#control
#Expend
class BakeTemplate(enum.Enum):
      '''expend  this will have other template
     
      '''
      One = 'one' # func : BakeNodeTreeTemplate.BakeNodeTreeTemplate0
   




template_id = str('template_')

bakeTemplates = [

   (template_id +str(BakeTemplate.One),str(BakeTemplate.One),str(BakeTemplate.One),'MOD_CLOTH',0),



]




class UVTextureLayer(bpy.types.PropertyGroup):

    coverObjName : bpy.props.StringProperty(
       name="coverObjName",
       description="CoverObjName",
       default="Default",
       maxlen=128

    ) 

    bakeObjName : bpy.props.StringProperty(
       name="bakeObjName",
       description="BakeObjName",
       default="Default",
       maxlen=128

    )
   
    
    blendMode : bpy.props.EnumProperty(
      
       items= modes,
       name="blendMode",
       description="uv_texture layer blendMode",
       default= blend_id + str(BlendMode.Normal),
       
      
    ) 

    isUseAlphaTexture : bpy.props.BoolProperty(
       
       name="isUseAlphaTexture",
       description="using AlphaTexture is or not",
       default=False

    )

    alphaFilePath : bpy.props.StringProperty(
 
      name="alphaFilePath",
      description= "alpha image filepath",
      default= ""
       
    )

    bakeTemplateType : bpy.props.EnumProperty(

      items= bakeTemplates,
      name= "bakeTemplate",
      description= 'bake image template make node tree func',
      default= template_id + str(BakeTemplate.One),
     



    )




#expend (all effect enum)
alltypes =  [

    (blur_id + str(BlurType.Null),str(BlurType.Null),str(BlurType.Null),'ALIGN_JUSTIFY',0),
    (blur_id + str(BlurType.Gaussian),str(BlurType.Gaussian),str(BlurType.Gaussian),'ALIGN_JUSTIFY',1),
    (blur_id + str(BlurType.Box),str(BlurType.Box),str(BlurType.Box),'ALIGN_JUSTIFY',2),
    (strock_id + str(Stroke.Base),str(Stroke.Base),str(Stroke.Base),'ALIGN_JUSTIFY',3),

   







 ] #blurTypes + strocks    # + ......
                   

def rUpdate(self,context):
   
   scene = bpy.context.scene
   stack = getattr(scene,'Image_stack_list' + str(scene.layer_choose_index))
   stack[scene.stack_choose_index].r = getattr(self,'Efr')


def xblurUpdate(self,context):
   
   scene = bpy.context.scene
   stack = getattr(scene,'Image_stack_list' + str(scene.layer_choose_index))
   stack[scene.stack_choose_index].xblur = getattr(self,'Efxblur')


def yblurUpdate(self,context):

   scene = bpy.context.scene
   stack = getattr(scene,'Image_stack_list' + str(scene.layer_choose_index))
   stack[scene.stack_choose_index].yblur = getattr(self,'Efyblur')


def strockweithUpdate(self,context):

   scene = bpy.context.scene
   stack = getattr(scene,'Image_stack_list' + str(scene.layer_choose_index))
   stack[scene.stack_choose_index].strockweith = getattr(self,'Efstrockweith')


def colorUpdate(self,context):

   scene = bpy.context.scene
   stack = getattr(scene,'Image_stack_list' + str(scene.layer_choose_index))
   stack[scene.stack_choose_index].color = getattr(self,'Efcolor')


#expend UVImage_stack_item
def regisiterItemAttrs():

   setattr(bpy.types.Scene,'Efr',bpy.props.FloatProperty(

                                name= 'Efr',
                                default= 1.50,
                                min= 0.0,
                                update= rUpdate

                              ))

   setattr(bpy.types.Scene,'Efxblur',bpy.props.IntProperty(

                                name='Efxblur',
                                default= 1,
                                min= 0, 
                                update= xblurUpdate 

                              ))

   setattr(bpy.types.Scene,'Efyblur',bpy.props.IntProperty(

                                name= 'Efyblur',
                                default= 1,
                                min= 0,
                                update= yblurUpdate

                              ))

   setattr(bpy.types.Scene,'Efstrockweith',bpy.props.IntProperty(

                                name= 'Efstrockweith',
                                default= 1,
                                min= 0,
                                update= strockweithUpdate
 
                              ))

   setattr(bpy.types.Scene,'Efcolor',bpy.props.FloatVectorProperty(

                                name= 'Efcolor',
                                default= (0.0,0.0,0.0),
                                min= 0.0,
                                max= 255.0,
                                update= colorUpdate

                               ))

# expend
# draw funcs


def NullDraw(scene,layout : bpy.types.UILayout,context):
    
    box = layout.box()
    row1 = box.row()
    row1.label(text= 'null')


def GaussianDraw(scene,layout : bpy.types.UILayout,context):

    box = layout.box()
    row1 = box.row()
    row1.prop(data= scene,property= 'Efr',text='GaussianRadius')
   
def BoxDraw(scene,layout : bpy.types.UILayout,context):

    box = layout.box()
    row1 = box.row()
    row1.prop(data= scene,property= 'Efxblur',text= 'box xblur') 
    row1.prop(data= scene,property= 'Efyblur',text= 'box yblur')


def StrockBaseDraw(scene,layout : bpy.types.UILayout,context):

    box = layout.box()
    row1 = box.row()
    row1.prop(data= scene,property= 'Efstrockweith',text= 'strock weith')
    row1.prop(data= scene,property= 'Efcolor',text= 'strock color')



# expend
# enum and draw func dict 
drawfuncs : dict[str,Any] = {

   blur_id + str(BlurType.Null) : NullDraw,
   blur_id + str(BlurType.Gaussian) : GaussianDraw,
   blur_id + str(BlurType.Box) : BoxDraw,
   strock_id + str(Stroke.Base) : StrockBaseDraw,



    


}





# --------------------


#expend
class UVImage_stack_item(bpy.types.PropertyGroup):
    
    stackActive : bpy.props.BoolProperty(

      name= 'stackActive',
      description= 'stack_item_active',
      default= True

    )

    effectType : bpy.props.EnumProperty(

      items= alltypes,
      name= 'effectType',
      description= 'all effect enums',
      default= 'None'

    )

    # a pool of parameters for all controls

    # Gaussian
    r : bpy.props.FloatProperty(

      name= 'r',
      default= 1.50,
      min= 0.0

    )

    # Box
    xblur : bpy.props.IntProperty(

      name='xblur',
      default= 1,
      min= 0

    )

    # Box
    yblur : bpy.props.IntProperty(

      name= 'yblur',
      default= 1,
      min= 0

    )

    # Strock Base
    strockweith : bpy.props.IntProperty(

      name= 'strockweith',
      default= 1,
      min= 0

    )
    
    # Strock Base
    color : bpy.props.FloatVectorProperty(

      name= 'color',
      default= (0.0,0.0,0.0),
      min= 0.0,
      max= 255.0

    )
