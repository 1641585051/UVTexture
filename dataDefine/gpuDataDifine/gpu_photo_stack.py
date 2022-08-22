
from typing import Any

from mars.core import base

from mars import tensor as ten

import numpy as np

from ...dataDefine import ControlAlgorithms

##  CUDA  ##
def returnConditionInZ(self,stackElementCount : int, shape : list[int],condition,step : int = 1,start : int = 0):
           
      array = np.empty(shape=(shape[0],shape[1],1),dtype= bool)
      array.fill(False)
           
      for i in range(start, (4 * stackElementCount),step):

         tem = np.empty(shape=(shape[0],shape[1],1),dtype= bool)
                 
         if condition(i,stackElementCount):
               
            tem.fill(True)

         else:

            tem.fill(False)

            array = ten.concatenate((array,tem),axis=2)

         array = np.delete(arr= array,obj= 0,axis=2) 

         return array.tolist()   



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
      
       shape = stack.shape   

       def con(i,stackElementCount):
         trueIndex = 4 * (stackElementCount -1)
         return i >= trueIndex

       ten.compress(returnConditionInZ(stackElementCount= stackElementCount,shape=shape,condition= con),stack,axis= 2,out=self.gpuImage).execute()


       
   

class gpuImageStack:
    '''this strack use cuda ,because mars use cuda \n
    
       and data color use rgb mode \n
       (0,255)\n

       Data is stored by differences \n 
       a,b,c is image \n
       stacks (0,1,2) is (a, b-a, c-b) b = a + (b-a) \n
       ... c = a + (b-a) + (c-b) \n
       .. \n


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
      

    def __CompositeResults__(self):

      shape = self.__stackgpudata.shape

      tem :ten.Tensor = ten.zeros(shape=(shape[0],shape[1],4),dtype= np.float32,gpu=True)

      def con(i,stackElementCount):
          
          return i < stackElementCount

      tem2 : ten.Tensor = ten.zeros(shape=(shape[0],shape[1],1),dtype= np.float32,gpu=True)

      result : ten.Tensor = ten.empty(shape=(shape[0],shape[1],1),dtype= np.float32,gpu=True)

      for ind in range(4): # rgba

          ten.compress(returnConditionInZ(stackElementCount= len(self.__stacks),shape=shape,condition= con,step=4,start= ind),self.__stackgpudata,axis= 2,out=tem).execute()
          tem.execute()

          ten.sum(tem,axis=2,dtype=np.float32,out= tem2).execute()
          tem2.execute()
          ten.stack(tensors= (result,tem2),axis=2,out= result).execute()
          
      
      return result


    def __updateStackData__(self,name :str):
      
      data = self.__stacks[name]

      # width and heigth is not different
      # ...
      if data.width != self.__width or data.height != self.__height:

         #tempdata = ten.base.to_cpu(data.gpuImage) 
         #array : np.ndarray = tempdata.to_numpy()
         #from ....UVTexture.tools import uv_cv_tools 
         #scaleArr = uv_cv_tools.scaleImage(array= array,old_wdith= data.width,old_height= data.height,new_width= self.__width,new_height= self.__height)
         
         scaleArr = ControlAlgorithms.CImageScaling(data.gpuImage,new_width= self.__width,new_height= self.__height)
         # change uv_cv_tools scaleImage to ControlAlgorithms.CImageScaling
        
         data.gpuImage = scaleArr
      
      oldImage : ten.Tensor = self.__CompositeResults__()     
  
      self.GetDifferenceImage(image0= oldImage,image1= data.gpuImage)
      # Data is stored by differences 
      # a,b,c is image
      # stacks (0,1,2) is (a, b-a, c-b) b = a + (b-a)
      # ... c = a + (b-a) + (c-b)
      #..
      

      tem : ten.Tensor = ten.dstack((self.__stackgpudata,data.gpuImage))
      tem.execute()
      self.__stackgpudata = ten.tensor(data= tem.to_numpy(),gpu= True) 
      
      self.__stackgpudata.execute()

      data.updateData(self.__stackgpudata,self.__imageOperatorNames.count)

      
    def add(self,operatorName: str,data :gpuImageDef):
       
       self.__imageOperatorNames.append(operatorName)
       
       self.__stacks[operatorName] = data

       self.__updateStackData__(operatorName)


    def __removeData__(self):

       delIndex = (len(self.__imageOperatorNames) -1) * 4 - 1

       dellist = list((delIndex + ind for ind in range(4)))
       
       tem :ten.Tensor = ten.delete(arr= self.__stackgpudata,obj=dellist,axis =2)
       tem.execute()
       self.__stackgpudata = ten.tensor(data =tem.to_numpy(),gpu= True)
       self.__stackgpudata.execute()
       

    def remove(self):
        ''' remove lase element'''
        if len(self.__imageOperatorNames) != 0 and len(list(self.__stacks.keys())) != 0:
           item = self.__imageOperatorNames.pop(len(self.__imageOperatorNames) -1)
           
           self.__removeData__()
           self.__stacks.pop(item)
           
           
    def getlastName(self):
        if len(self.__imageOperatorNames) != 0:

           return self.__imageOperatorNames[len(self.__imageOperatorNames) -1]
        else:
           return None
    

    def getlastData(self):
          keys = list(self.__stacks.keys())
          if len(keys) != 0:
             
             return self.__stacks[keys[len(keys) -1]]


    def removeAssociateData(self,operName: str):
         '''this mains 
         
            datas = {0: 00, 1:11 ,2:22 ....}
         
            datas.removeAssociateData(1)

            > datas : {0,00}

            this func will delete 1 and all data behind

         '''    
         de_ind = self.__imageOperatorNames.index(operName) 
         de_lis = list((de_ind + ind for ind in range(len(self.__imageOperatorNames) - de_ind)))

         for ind in de_lis:
            self.__stacks.pop(self.__imageOperatorNames[ind])

         de_obj = list((de_ind *4 + ind2 for ind2 in range((self.__imageOperatorNames)*4  - de_ind *4)))

         tem : ten.Tensor = ten.delete(arr= self.__stackgpudata,obj =de_obj,axis=2)
         tem.execute()
         self.__stackgpudata = ten.tensor(data= tem.to_numpy(),gpu=True)
         self.__stackgpudata.execute()

           
    def GetDifferenceImage(self,image0 : ten.Tensor,image1 : ten.Tensor):
        '''difference imai - ima0 :  inage1 as result
           
        '''
        ten.subtract(x1=image1,x2=image0,out=image1).execute()
        

    def ResetStackSize(self,width,height):

       self.__width = width
       self.__height = height  
       
       self.__stackgpudata = ControlAlgorithms.CImageScaling(self.__stackgpudata,new_width= width,new_height= height)

       for value in self.__stacks.values():
           value.width = width
           value.height = height
           value.gpuImage = ControlAlgorithms.CImageScaling(value.gpuImage,new_width= width,new_height= height)


       


##  CUDA  ##
       


##  AMD ##









##  ----------  ##