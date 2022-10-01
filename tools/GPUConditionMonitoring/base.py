import bpy


from .. import gpuEnv 
import pynvml


GB : int = 1073741824



class UVTexture_OT_OpenGPUConsumption(bpy.types.Operator):

    bl_idname: str = 'object.opengpuconsumption'
    bl_label: str = "open GPU Consumption"
    def getGPUMessage(self):
     
        scene = bpy.context.scene
        
        out0 : str = "-/-"
        out1 : str = "0%"

        if gpuEnv.NVAmdorOther:
      
          pynvml.nvmlInit()

          gpu_id=0
          handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
          info = pynvml.nvmlDeviceGetMemoryInfo(handle)

          gpu_Total : str = str(round(info.total / GB,3)) + ' GB'
          gpu_Used : str = str(round(info.used / GB,3)) + ' GB'
           
          scene.GPUVideoMemoryConsumption = gpu_Used + '/' + gpu_Total  

          tem0 = int(str(info.total))
          tem1 = int(str(info.used))
          tem2 : float = (tem1 / tem0) * 100
  
          scene.GPUUsage = str(round(tem2,3)) + '%' 

          pynvml.nvmlShutdown()

        else:

          pass



    def execute(self, contex):
       
        self.getGPUMessage()

        #bpy.ops.object.stackcompute('INVOKE_DEFAULT')
      
        return {"FINISHED"}



class UVTexture_PT_GPUPanel(bpy.types.Panel):

    bl_idname: str = 'UVTexture_PT_GPUPanel'
    bl_label: str = "gpu panel"

    #bl_category: str = 'gpu'

    bl_region_type :str = 'UI'
    bl_space_type :str =  "VIEW_3D"

    bl_parent_id: str = 'UVTexture_PT_Base'

    def draw(self, context):
        
        scene = bpy.context.scene

        layout = self.layout  
        box = layout.box()
        row0 = box.row()

        row0.operator('object.opengpuconsumption',text= 'openGPUC') 
        row0.prop(data= scene,property= 'GPUUsage',text= 'GPUUsage')
        row0.prop(data= scene,property= 'GPUVideoMemoryConsumption',text= 'GPU_VMC')

    ...
