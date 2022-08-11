from operator import index
from re import T
from typing import Any

from mars.core import base




from ....UVTexture.mars import tensor as ten

from ....UVTexture import numpy as np


##  CUDA  ##

class gpuImageDef:
    
    width: int = 1024
    height: int = 1024 

    gpuImage : ten.Tensor = None

    
    def __init__(self,image_width: int,image_height: int,is64Bit: bool = False) -> None:
       
       self.width = image_width
       self.height = image_height
       
       type_ :Any 
       if is64Bit:
          type_ = np.float64
       else:
          type_ = np.float32

       r = np.zeros(shape=(image_width,image_height),dtype= type_)
       g = np.zeros(shape=(image_width,image_height),dtype= type_)
       b = np.zeros(shape=(image_width,image_height),dtype= type_)
       a = np.zeros(shape=(image_width,image_height),dtype= type_)
     
       self.gpuImage = ten.tensor(data=np.array([r,g,b,a]),gpu=True)
       
       self.gpuImage.execute()
       
       

    def updateData(self,stack: ten.Tensor,stackElementCount: int):
      
       def returnCondition():
           trueIndex = 4 * (stackElementCount -1)
           boollist = [False] * 4 * stackElementCount
           for i in range(4 * stackElementCount):
               if i >= trueIndex:
                  boollist[i] = True

           return boollist       


       self.gpuImage = ten.tensor(data =ten.compress(returnCondition(),stack,axis= 2),gpu=True)

       self.gpuImage.execute()

       
   



   

  
class gpuImageStack:
    '''this strack use cuda ,because mars use cuda
    
       and data color use rgb mode
    '''

    __width : int = 1024
    __height : int = 1024 

    __stacks : dict[str,gpuImageDef] = None

    __imageOperatorNames : list[str] = None
    '''names is stackes key ----> gpuImageDef = stacks[name] '''

    __stackgpudata :ten.Tensor = None

    
    def __init__(self,stackItemWidth = 1024,stackItemheight = 1024,is64Bit: bool = False):
      
      self.__width = stackItemWidth
      self.__height = stackItemheight

      self.__stacks = dict()

      self.__imageOperatorNames = list()        
    
      type_ :Any 
      if is64Bit:
          type_ = np.float64
      else:
          type_ = np.float32

      r = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= type_)
      g = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= type_)
      b = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= type_)
      a = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= type_)
     
       
      self.__stackgpudata = ten.tensor(data=[r,g,b,a],dtype= type_,gpu= True)
      
      self.__stackgpudata.execute()
      

    def __updateStackData__(self,name :str):
      
      data = self.__stacks[name]

      # width and heigth is not different
      # ...
      if data.width != self.__width or data.height != self.__height:

         
         tempdata = ten.base.to_cpu(data.gpuImage) 
         array : np.ndarray = tempdata.to_numpy()
         from ....UVTexture.tools import uv_cv_tools 

         scaleArr = uv_cv_tools.scaleImage(array= array,old_wdith= data.width,old_height= data.height,new_width= self.__width,new_height= self.__height)

         data.gpuImage = ten.tensor(data= scaleArr,dtype= ten.float64,gpu=True)

         
         ...

      self.__stackgpudata = ten.tensor(data= ten.dstack((self.__stackgpudata,data.gpuImage)),gpu= True) 
      
      self.__stackgpudata.execute()

      data.updateData(self.__stackgpudata,self.__imageOperatorNames.count)

      
    def add(self,operatorName: str,data :gpuImageDef):
       
       self.__imageOperatorNames.append(operatorName)
       
       self.__stacks[operatorName] = data

       self.__updateStackData__(operatorName)


    def __removeData__(self):

       delIndex = (self.__imageOperatorNames.count() -1) * 4 - 1

       dellist = list((delIndex + ind for ind in range(4)))
       
       self.__stackgpudata = ten.tensor(data =ten.delete(arr= self.__stackgpudata,obj=dellist,axis =2),gpu= True)
       self.__stackgpudata.execute()
       

    def remove(self):
        ''' remove lase element'''
        if self.__imageOperatorNames.count() != 0 and list(self.__stacks.keys()).count() != 0:
           item = self.__imageOperatorNames.pop(self.__imageOperatorNames.count() -1)
           
           self.__removeData__()
           self.__stacks.pop(item)
           
           


    def getlastName(self):
        if self.__imageOperatorNames.count() != 0:

           return self.__imageOperatorNames[self.__imageOperatorNames.count() -1]
        else:
           return None
    

    def getlastData(self):
          keys = list(self.__stacks.keys())
          if keys.count() != 0:
             
             return self.__stacks[keys[keys.count() -1]]


    def removeAssociateData(self,operName: str):
         '''this mains 
         
            datas = {0: 00, 1:11 ,2:22 ....}
         
            datas.removeAssociateData(1)

            > datas : {0,00}

            this func will delete 1 and all data behind

         '''    
         de_ind = self.__imageOperatorNames.index(operName) 
         de_lis = list((de_ind + ind for ind in range(self.__imageOperatorNames.count() - de_ind)))

         for ind in de_lis:
            self.__stacks.pop(self.__imageOperatorNames[ind])

         de_obj = list((de_ind *4 + ind2 for ind2 in range(self.__imageOperatorNames.count()*4  - de_ind *4)))

         self.__stackgpudata = ten.tensor(data= ten.delete(arr= self.__stackgpudata,obj =de_obj,axis=2),gpu=True)
         self.__stackgpudata.execute()

           


##  CUDA  ##
       


##  ...       