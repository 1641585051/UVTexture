
from this import d
import bpy
from ..UVOperators import UV_operators



class UVTexture_PT_output_config(bpy.types.Panel):
    #bl_idname: str = "UVTexture_PT_output_configk"
    bl_label: str = "output config"

    bl_region_type :str = 'UI'
    bl_space_type :str =  "VIEW_3D"
    bl_parent_id: str = 'UVTexture_PT_Base'


    def draw(self, context):

      scene = bpy.context.scene
      
      layout = self.layout

      one = layout.row()
 
      one.prop(scene,'float32',text= "isUsefloat64")
      one.prop(scene,'textureSideLength',text= "textureSideLength",icon= "SHADING_BBOX")
      
      two = layout.row()

      two.prop(scene,'mappingSampleNums',text= 'SampleNums',icon= 'OUTLINER_DATA_LIGHTPROBE') 


class UVTexture_UL_List_Image_stack(bpy.types.UIList):

   bl_idname: str = 'Image_stack_list'
   
   use_filter_show: bool = True
   use_filter_sort_alpha: bool = True
   list_id: str = 'UV_Texture_image_stack_part'

   def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
      
      #scene = bpy.context.scene

      row = layout.row()

      #layerIndex = scene.layer_choose_index
 
      #stack = getattr(scene,'Image_stack_list' + str(layerIndex))

      #effectType = stack[index].effectType

      row.operator('object.recalculateimagestack',text= "",icon= 'FILE_REFRESH')

      row.prop(data= data, property='effectActive' + str(index),text= "") 

      row2 = layout.row() 
      row2.separator()
      
      row2.prop(data= data,property= 'effectType' + str(index),text="",icon= 'FILE_IMAGE')

       


def updateStack(row : bpy.types.UILayout):

      scene = bpy.context.scene
      
      box = row.box()

      if scene.layer_choose_index > -1:

         box.template_list(

               listtype_name= UVTexture_UL_List_Image_stack.bl_idname,
               list_id= UVTexture_UL_List_Image_stack.list_id,
               dataptr= scene,
               propname= 'Image_stack_list' + str(scene.layer_choose_index),
               active_dataptr= scene,
               active_propname= 'Image_stack_index' + str(scene.layer_choose_index),

            )
            


class UVTexture_PT_layer_Image_stack(bpy.types.Panel):
   #bl_idname: str = "UVTexture_PT_layer_Image_stack"
   bl_label: str = "image stack"

   #bl_category: str = 'stack'
   bl_region_type :str = 'UI'
   bl_space_type :str =  "VIEW_3D"
   bl_parent_id: str = 'UVTexture_PT_Base'


   def draw(self, context):

      scene = bpy.context.scene

      layout = self.layout
      row = layout.row()
      row.label(text= "image stack")
      
      row2 = layout.row()
      row2.prop(scene,'layer_choose_index',text="eding index",icon= 'FILE_IMAGE')

      row2.operator(operator= 'object.changechooseindexbyroller',text="",icon= 'MOUSE_MMB')

      row3 = layout.row()

      updateStack(row= row3) 
  





class UVTexture_UL_List_uv_tree(bpy.types.UIList):
   
   bl_idname: str = "UVTexture_List_uv_tree" 
   #layout_type = "DEFAULT"
   use_filter_show: bool = True
   use_filter_sort_alpha: bool = True

   list_id: str = "UV_Texture_Tree_part"
   
   
   def draw_item(self,context,layout,data,item,icon: int,active_data,active_property,index,flt_flag):
      
      if self.layout_type in {"DEFAULT", "COMPACT"}:
           
         box = layout.box()
         
         row = box.row()

         row.prop(data= data,property= 'active_' + str(index),text="")
         # blendMode More important ,so put fist row 
         row.prop(data= data,property= 'blendMode_' + str(index)) 

         row.prop(data= data,property= 'layerName_' + str(index),text = "LayerName")
         
         row2 = box.row()
         othersettings = row2.box()
         
         settingrow = othersettings.row()
         settingrow.separator()
         settingrow.prop(data= data,property= 'isUseAlphaTexture_' + str(index),text="alpha")
         settingrow.prop(data= data,property= 'coverObjName_' + str(index),text="coverName")
         settingrow.operator(operator='object.eyetropper_coverobjname',text="",icon='EYEDROPPER')
      
         settingrow2 = othersettings.row()
         settingrow2.prop(data= data,property= 'bakeTemplateType_' + str(index))
         



      elif self.layout_type in {"GRID"}:
           pass

   
  



class UVTexture_PT_Base(bpy.types.Panel):
   bl_idname: str = "UVTexture_PT_Base"
   bl_label: str = "uv_Texture"

   bl_category: str = "uv"
   bl_region_type :str = "UI"
   bl_space_type :str = "VIEW_3D"
  # bl_context = "object"
   


   def draw(self, context):
      
      layout = self.layout
      layout.label(text= 'UV_Texture')
      row = layout.row()
      row.operator(UV_operators.UVTexture_OT_RunUVTextureOperator.bl_idname,text= "Run UVTexture")
      layout.separator()
      box = layout.box()
      box.label(text= 'uv_tree')
      
      listrow = box.row()

      scene = context.scene

      listrow.template_list(
         
         UVTexture_UL_List_uv_tree.bl_idname,
         UVTexture_UL_List_uv_tree.list_id,
         scene,
         "uv_texture_list",
         scene,
         "uv_texture_list_index",
         rows= scene.uilistData.layerMinNum,
         maxrows= scene.uilistData.layerMaxNum

         )

      subrow = listrow.column()   
      subrow.operator(operator= 'object.createlayer',text= "",icon="ADD")
      
      subrow.operator(operator= 'object.deletelayer',text="",icon="REMOVE")
      




