
import os
from sys import stdout
import gpu
import operator
import subprocess


from ..buildenv import base

NV : str = 'NVIDIA'

AMD : str = 'AMD'

NVAmdorOther : bool = None
''' true is NVIDIA or AMD,false is other

    since cupy supports NV and AMD computing libraries,it does
    not distinguish between the two.  


'''

def makeSureGPUEnv():
  
  global NVAmdorOther
  gpu_platform = gpu.platform.vendor_get()
  if operator.contains(gpu_platform,NV) | operator.contains(gpu_platform,AMD):
     
     NVAmdorOther = True


  else:
     NVAmdorOther = False

  import taichi as ti 
  ti.init(arch=ti.gpu)


#cuda version list
# example CUDA Version: 11.4
 
   #EXPEND#
cudav_dict = {
   
   10.2: 'cupy-cuda102',
   11.0: 'cupy-cuda110',
   11.1: 'cupy-cuda111',
   11.2: 'cupy-cuda11x',
   11.4: 'cupy-cuda114',
   11.6: 'cupy-cuda116',

   


   #laster


   }
'''cudav_list need update from https://github.com/cupy/cupy '''



def getCupy():

   path = base.rootPath
   exedir = base.findBlenderfromJson(path + "buildenv" + os.path.sep + "env.json")
   packDir = base.getPackagesDir(exeDir= exedir)
   pipexepath = packDir + os.path.sep + 'pip' + os.path.sep + '__main__.py' 

   isdown = base.getDownloadCupy(path + "buildenv" + os.path.sep + "env.json") 

   if isdown == 0:

   # if gpu is NV, make sure Cuda Version, and download cupy (vision)---
      if NVAmdorOther:
         
         command = 'nvidia-smi'
         open_process = subprocess.Popen(

                        command,
                        stdout= subprocess.PIPE,
                        shell= True

                        )
         
         cmd_out = open_process.stdout.read()
         open_process.stdout.close()
         simstr = cmd_out.decode(encoding= "UTF-8") 
         
         for item in cudav_dict:

            
            if operator.contains(simstr,'CUDA Version:'.replace(' ','\ ') + ' ' + str(item)):

                  sub_process = subprocess.Popen(

                           exedir.replace(' ','\ ') + ' ' + pipexepath.replace(' ','\ ') + ' ' + 'install ' + '--target=' + packDir.replace(' ','\ ') + ' ' + cudav_dict[item],
                           shell= True

                           )

                  sub_process.wait()
                  base.setDownloadCupy(path + "buildenv" + os.path.sep + "env")



      else:

         pass   


   ...