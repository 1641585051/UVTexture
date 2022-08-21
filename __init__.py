import sys
import importlib
from typing import Any

import bpy



bl_info = {
    "name" : "UV_Texture",
    "author" : "FlagYoung",
    "description" : "",
    "blender" : (3, 20, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


##
# import files
# ##---------------

from .UI import UV_UI
from .UVOperators import UV_operators,UV_UI_Operators
from .UVMapping import UVMappingOperator
from .dataDefine import DataProperty ,UVListLayer


#----------------

classes : dict[int,Any] = {
  
  0: UV_UI.UVTexture_PT_Base,
  1: UV_operators.UVTexture_OT_RunUVTextureOperator,
  2: UV_UI.UVTexture_UL_List_uv_tree,
  3: UV_UI_Operators.UITree_OT_createItem,
  4: UV_UI_Operators.UITree_OT_deleteItem,
  5: UV_operators.UVTexture_OT_InitOperator,
  6: UV_operators.UVTexture_OT_ObjectUVMapping,
  7: UVMappingOperator.UVTexture_OT_UvMappingInitDataOperator,
  8: UVMappingOperator.UVTExture_OT_UvMappingCalculateProjectionValue,
  9: UV_UI_Operators.UITree_OT_eyetropper_CoverObjName,
  10: UV_UI.UVTexture_PT_layer_Image_stack,
  11: UV_operators.UVTexture_OT_Image_Stack_Compute,
  12: UV_UI.UVTexture_PT_output_config,
  

 
## expend





}

dataClasses = {

  0: DataProperty.UVTree_list_item,
  1: UVListLayer.UVTextureLayer, 
  2: DataProperty.UVBakeImageConfig,
  3: DataProperty.BakeExtendTemplateData,
  4: DataProperty.UVTextureOutPutConfig,
  5: DataProperty.SystemData,
  6: UVListLayer.UVImage_stack_item,
  




}



def registerFunc(classes : dict ,is_unRegister : bool = False):
    
    values = classes.values()
    valueList = list(values)
    

    for cl in valueList:
        if(is_unRegister):
          bpy.utils.unregister_class(cl)
        else:
          bpy.utils.register_class(cl)  
    

from .tools import gpuEnv,error

def register():


    gpuEnv.makeSureGPUEnv()

    registerFunc(dataClasses,False)
    DataProperty.UVTextureProperties()
    registerFunc(classes,False)

    bpy.types.Scene.uilistData.init()

 
def unregister():

    

    registerFunc(classes,True)
    bpy.types.Scene.uilistData.unload()
    
    registerFunc(dataClasses,True)

    




if __name__ == "__main__":
    
    sys.excepthook = error.uvTextureExehook
    register()
