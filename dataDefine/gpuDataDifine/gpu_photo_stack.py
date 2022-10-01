

from typing import Any

import os 
import bpy

import cupy as ten


import numpy as np

from ...dataDefine import ControlAlgorithms

def returnConditionInZ(stackElementCount : int, shape : list[int],condition,step : int = 1,start : int = 0):
           
      array : ten.ndarray = ten.full(shape=(shape[0],shape[1],1),fill_value= False,dtype= bool)
                 
      for i in range(start, (4 * stackElementCount),step):

         tem : ten.ndarray = None

         if condition(i,stackElementCount):
               
            tem = ten.full(shape=(shape[0],shape[1],1),fill_value= True,dtype= bool)

         else:

            tem = ten.full(shape=(shape[0],shape[1],1),fill_value= True,dtype= bool)

            array = ten.concatenate((array,tem),axis=2)

         array = ten.delete(arr= array,obj= 0,axis=2) 

         return array



class gpuImageDef:
    
    width: int = 1024
    height: int = 1024 

    gpuImage : ten.ndarray = None

    
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
     
       self.gpuImage = ten.array(data=np.array([r,g,b,a]))
       
       

    def updateData(self,stack: np.ndarray,stackElementCount: int):
      
       shape = stack.shape   

       def con(i,stackElementCount):
         trueIndex = 4 * (stackElementCount -1)
         return i >= trueIndex

       ten.compress(returnConditionInZ(stackElementCount= stackElementCount,shape=shape,condition= con),stack,axis= 2,out=self.gpuImage)


       
   

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

    __type = np.float32

    __stackIndex = -1

    __stacks : dict[str,gpuImageDef] = None

    __imageOperatorNames : list[str] = None
    '''names is stackes key ----> gpuImageDef = stacks[name] '''

    __stackgpudata : ten.ndarray = None

    
    def __init__(self,stackIndex : int,stackItemWidth : int = 1024,stackItemheight : int = 1024,is64Bit: bool = False):
      
      self.__width = stackItemWidth
      self.__height = stackItemheight

      self.__stacks = dict()

      self.__stackIndex = stackIndex

      self.__imageOperatorNames = list()        
    
      self.__type = np.float32

      if is64Bit:
          self.__type = np.float64
      else:
          self.__type = np.float32

      r = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= self.__type)
      g = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= self.__type)
      b = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= self.__type)
      a = np.zeros(shape=(stackItemWidth,stackItemheight),dtype= self.__type)
     
      self.__imageOperatorNames.append('bakeImage') 

      self.__stackgpudata = ten.array(obj=np.dstack(tup= (r,g,b,a)),dtype= self.__type)
      
   
      

    def __CompositeResults__(self):

      shape = ten.shape(self.__stackgpudata)

      tem :ten.ndarray = ten.zeros(shape=(shape[0],shape[1],4),dtype= self.__type)

      def con(i,stackElementCount):
          
          return i < stackElementCount

      tem2 : ten.ndarray = ten.zeros(shape=(shape[0],shape[1],1),dtype= self.__type)

      result : ten.ndarray = ten.empty(shape=(shape[0],shape[1],1),dtype= self.__type)

      for ind in range(4): # rgba

          ten.compress(returnConditionInZ(stackElementCount= len(self.__stacks),shape=shape,condition= con,step=4,start= ind),self.__stackgpudata,axis= 2,out=tem)
         
          ten.sum(tem,axis=2,dtype= self.__type,out= tem2)
          
          ten.stack(tensors= (result,tem2),axis=2,out= result)
          
      
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
        
         data.gpuImage = ten.array(data= scaleArr.to_numpy(),dtype= self.__type,gpu= True)
      
      oldImage : ten.ndarray = self.__CompositeResults__()     
  
      data.gpuImage = self.GetDifferenceImage(image0= oldImage,image1= data.gpuImage)
      # Data is stored by differences 
      # a,b,c is image
      # stacks (0,1,2) is (a, b-a, c-b) b = a + (b-a)
      # ... c = a + (b-a) + (c-b)
      #..
      
      self.__stackgpudata = ten.dstack((self.__stackgpudata,data.gpuImage))
      

      data.updateData(self.__stackgpudata,self.__imageOperatorNames.count)

      
    def add(self,operatorName: str,data :gpuImageDef):
       
       self.__imageOperatorNames.append(operatorName)
       
       self.__stacks[operatorName] = data

       self.__updateStackData__(operatorName)


    def __removeData__(self):

       delIndex = (len(self.__imageOperatorNames) -1) * 4 - 1

       dellist = list((delIndex + ind for ind in range(4)))
       
       self.__stackgpudata = ten.delete(arr= self.__stackgpudata,obj=dellist,axis =2)
       


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

            but don't delete any elements of operatorNames 
         '''    
         de_ind = self.__imageOperatorNames.index(operName) 
         de_lis = list((de_ind + ind for ind in range(len(self.__imageOperatorNames) - de_ind)))

         for ind in de_lis:
            self.__stacks.pop(self.__imageOperatorNames[ind])

         de_obj = list((de_ind *4 + ind2 for ind2 in range((self.__imageOperatorNames)*4  - de_ind *4)))

         self.__stackgpudata = ten.delete(arr= self.__stackgpudata,obj =de_obj,axis=2)
     
        

           
    def GetDifferenceImage(self,image0 : ten.ndarray,image1 : ten.ndarray):
        '''difference imai - ima0 :  inage1 as result
           
        '''
        return ten.subtract(x1=image1,x2=image0)
        

    def ResetStackSize(self,width,height):

       self.__width = width
       self.__height = height  
       
       self.__stackgpudata = ControlAlgorithms.CImageScaling(self.__stackgpudata,new_width= width,new_height= height)

       for value in self.__stacks.values():
           value.width = width
           value.height = height
           value.gpuImage = ControlAlgorithms.CImageScaling(value.gpuImage,new_width= width,new_height= height)


    def SaveImageStack(self,layerIndex):

        config = np.ndarray(shape= 3,dtype=np.float32) 

        config[0] = self.__width
        config[1] = self.__height

        np.save(os.path.dirname(__file__) + os.sep + 'config ' + str(layerIndex) + '.npy',config)

        data = ten.asnumpy(self.__stackgpudata)

        np.save(os.path.dirname(__file__) + os.sep + 'data ' + str(layerIndex) + '.npy',data)
     
        

    def ReadImageStack(self,layerIndex):

        


       ...



    def RecalculateAllData(self,image : ten.ndarray,index : int):
      '''
      RecalculateAllData at this image stack 
      update all layer by new bake image   

      index : layer_choose_index
      
      '''
      tem = image

      self.removeAssociateData(self.__imageOperatorNames[1])

      import inspect

      scene = bpy.context.scene

      if len(self.__stacks) > 0: 

         stack = getattr(scene,'Image_stack_list' + str(index))
         item = stack[self.__stackIndex]
         
         # imageOperatorNames is UVListLayer.allType value
         for name in self.__imageOperatorNames:
            
            if name != 'bakeImage':
               func = ControlAlgorithms.all_effect_funcs[name]
               prameters : list[Any] = []
               spec = inspect.getfullargspec(func= func)

               for permeter in spec.args:
                  
                  if permeter != 'a':
                     prameters.append(getattr(item,permeter))

               tem = func(*prameters) 
               gpudef = gpuImageDef(image_width= ten.shape(tem)[0],image_height= ten.shape(tem)[1])
               gpudef.gpuImage = tem
               
               self.add(name,gpudef) 
     




    def SetBakeImage(self,image_ : np.ndarray,index : int,backgroundColor : tuple[float,float,float] = (0.0,0.0,0.0)):

   
      image : ten.ndarray = ten.array(data= image_,dtype= self.__type)
     
      # set -1 mask
      mskData = list(backgroundColor)
      mskData.append(255.0)
      arr = np.array(object = mskData ,dtype= np.float32) 
      arr.reshape(shape= (1,1,4))      
      
      temMask = ten.array(data= ten.asnumpy(arr),dtype= np.float32)
      
      maskBool = ten.equal(x1= image,x2= temMask)

      maskTen = ten.full(shape= ten.shape(image),fill_value= -1.0,dtype= np.float32)
      
      ten.take(a= maskTen,indices=maskBool,out= image)
      # ----------

      elements = ten.dsplit(a =self.__stackgpudata,indices_or_sections= 4)
      
      elements[0] = image
     
      tem : ten.ndarray = ten.hstack(tup =elements)

      self.__stackgpudata = tem

      self.__stacks[list(self.__stacks.keys())[0]] = gpuImageDef(image_width =self.__width,image_height= self.__height,is64Bit= (self.__type == np.float64))
      
      self.__stacks[0].gpuImage = image

      self.RecalculateAllData(image,index)

    def GetBakeImage(self):

       return self.__stacks[0].gpuImage

   
    def outputImageData(self):
       
       zeroTen = ten.full(shape= ten.shape(self.__stackgpudata),fill_value= 0.0,dtype= self.__type)

       maskTen = ten.full(shape= ten.shape(self.__stackgpudata),fill_value= False) 
       
      
       ten.equal(x1=self.__stackgpudata,x2= -1,out= maskTen)
       
       ten.take(a= zeroTen,indices= maskTen,out= self.__stackgpudata)

       images = ten.hsplit(a= self.__stackgpudata,indices_or_sections= 4)
       

       re :ten.ndarray = ten.full(shape= (ten.shape(self.__stackgpudata)[0],ten.shape(self.__stackgpudata)[0],4),fill_value= 0.0,dtype= self.__type) 
       
       reImages = list(images)
       for i in range(len(reImages)):

         ten.add(x1= re,x2= reImages[i],out= re)


       return re
      











##  ----------  ##