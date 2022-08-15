

import bpy


from ..dataDefine import DataProperty,UVListLayer

class UITree_OT_createItem(bpy.types.Operator):
    bl_idname: str = "object.createlayer"
    bl_label: str = "create layer"

    

    def execute(self, context):
        
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

        item.active = True

        item.layerName = 'layer_' + str(scene.uv_texture_list_index)
        
        setting = scene.uv_texture_settings.add()

        setting.coverObjName = ""
        setting.blendMode = UVListLayer.blend_id + str(UVListLayer.BlendMode.Normal)
        setting.isUseAlphaTexture = False
        setting.isUseBlur = False
        setting.blurType = UVListLayer.blur_id + str(UVListLayer.BlurType.Null)
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


class UITree_OT_moveItem(bpy.types.Operator):
    bl_idname: str = "object.movelayer"
    bl_label: str = "move layer"


    
            