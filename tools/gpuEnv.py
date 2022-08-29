
import gpu
import operator


NV : str = 'NVIDIA'

AMD : str = 'AMD'

NVorAmd : bool = None
''' true is NVIDIA ,false is AMD'''

def makeSureGPUEnv():
  
  global NVorAmd
  gpu_platform = gpu.platform.vendor_get()
  if operator.contains(gpu_platform,NV):
     NVorAmd = True
     pass

  elif operator.contains(gpu_platform,AMD):
     NVorAmd = False
     pass

  else:
     pass

  import taichi as ti 
  ti.init(arch=ti.gpu)
