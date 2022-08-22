

from typing import Any
import bpy


from ..dataDefine import DataProperty,UVListLayer

from ..dataDefine.gpuDataDifine import gpu_photo_stack
from ..tools import gpuEnv

image_stack_Struct : dict[int,Any] = {}


def getImageStackDict():

    return image_stack_Struct



class UVTree_OT_recalculate_image_stack(bpy.types.Operator):
    ''' recalculate all image stack effect '''


    bl_idname: str = "object.recalculateimagestack"
    bl_label: str = "recalculate image stack"
    
    def check(self, context) -> bool:
        ...


    def execute(self, context):
        
        
        
        
        return {"FINISHED"}




class UVTree_OT_change_choose_index_by_Roller(bpy.types.Operator):
    '''ctrl + left mouse is next layer,
       left mouse is before layer
    '''


    bl_idname: str = "object.changechooseindexbyroller"
    bl_label: str = "set choose index Ui element by roller"
    
    def check(self, context) -> bool:
       return True

    def invoke(self, context, event):
       
       if event.ctrl and event.type == 'LEFTMOUSE' :
            
          bpy.context.scene.layer_choose_index += 1
      
       elif event.type == 'LEFTMOUSE':
          
          bpy.context.scene.layer_choose_index -= 1

       return {"FINISHED"}
    



class UITree_OT_eyetropper_CoverObjName(bpy.types.Operator):
 
    bl_idname: str = "object.eyetropper_coverobjname"
    bl_label: str = "eyetropper coverObjName form 3D view by active Object"
    
    def check(self, context) -> bool:
        scene = bpy.context.scene
        
        return scene.layer_choose_index != -1


    def execute(self, context):

        scene = bpy.context.scene
        activeObj = bpy.context.active_object
        setattr(scene,'coverObjName_' + str(scene.layer_choose_index),activeObj.name)

        return {"FINISHED"}

  



class UITree_OT_createItem(bpy.types.Operator):
    bl_idname: str = "object.createlayer"
    bl_label: str = "create layer"

    def check(self, context) -> bool:
        scene = bpy.context.scene
        
        return len(scene.uv_texture_list) < 99

    def execute(self, context):
        

        global image_stack_Struct

        scene = bpy.context.scene

        item = scene.uv_texture_list.add() 
        scene.uv_texture_list_index +=1

        if len(scene.uv_texture_output_config) == 0:
               DataProperty.InitOutPutConfig()


        config = scene.uv_bake_image_config.add()
        config.width = scene.uv_texture_output_config[len(list(scene.uv_texture_output_config)) - 1].textureSideLength
        config.height = scene.uv_texture_output_config[len(list(scene.uv_texture_output_config)) - 1].textureSideLength
        config.color = (0.0,0.0,0.0)
        config.float32 = scene.uv_texture_output_config[len(list(scene.uv_texture_output_config.keys())) - 1].float32 

        if gpuEnv.NVorAmd:
                    # init CUDA context struct
                image_stack_Struct[scene.uv_texture_list_index] = gpu_photo_stack.gpuImageStack(
                                                                                                        
                                                                     stackItemWidth = config.width,
                                                                     stackItemheight= config.height,
                                                                     is64Bit= config.float32

                                                                  )
        else:
                    # AMD context struct 
            pass


        item.active = True

        item.layerName = 'layer_' + str(scene.uv_texture_list_index)
        
        setting = scene.uv_texture_settings.add()

        setting.coverObjName = ""
        setting.blendMode = UVListLayer.blend_id + str(UVListLayer.BlendMode.Normal)
        setting.isUseAlphaTexture = True
        setting.bakeTemplateType = UVListLayer.template_id + str(UVListLayer.BakeTemplate.Base)
        
        
        return {"FINISHED"}
    
    



class UITree_OT_deleteItem(bpy.types.Operator):
    bl_idname: str = "object.deletelayer"
    bl_label: str = "delete layer"

    @classmethod
    def poll(cls,context):
        scene = bpy.context.scene
        if len(scene.uv_texture_list) != 0:
            return True
        else:
            return False    

    def execute(self, context):

        scene = bpy.context.scene
        index = scene.uv_texture_list_index
        scene.uv_texture_list.remove(index)

        scene.uv_texture_list_index = min(max(0,index - 1),len(scene.uv_texture_list) - 1)

        return {"FINISHED"}



    
            