
import numpy as np
import taichi as ti
import mars.tensor as ten


##       CUDA         ##

#------------------------blendMode----------------------------#

# a down layer, b is up layer

# Normal

def CNormal(a :ten.Tensor ,b : ten.Tensor):

   return b 

# Darken
def CDarken(a :ten.Tensor,b :ten.Tensor):
  ''' reture a <= b => a or b <=a => b'''
  re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
  re.execute()  
  a1 = ten.zeros(shape= a.shape,dtype= np.bool8,gpu= True)
  a1.execute()
  b1 = ten.zeros(shape= b.shape,dtype= np.bool8,gpu= True)
  b1.execute()
  ten.less_equal(x1= a,x2= b,out= a1).execute()
  ten.less_equal(x1= b,x2= a, out= b1).execute()

  ten.compress(condition= a1,a= a,out= re).execute()
  ten.compress(condition= b1,a= b,out= re).execute() 

  return re

# Lighten
def CLighten(a :ten.Tensor,b :ten.Tensor):
  ''' reture a >= b => a or b >=a => b'''
  re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
  re.execute()  
  a1 = ten.full(shape= a.shape,fill_value= False,gpu=True)
  a1.execute()
  b1 = ten.full(shape= b.shape,fill_value= False,gpu= True)
  b1.execute()
  ten.greater_equal(x1= a,x2= b,out= a1).execute()
  ten.greater_equal(x1= b,x2= a, out= b1).execute()

  ten.compress(condition= a1,a= a,out= re).execute()
  ten.compress(condition= b1,a= b,out= re).execute() 


# Multiply
def CMultiply(a :ten.Tensor,b :ten.Tensor):
   
    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    ten.multiply(x1=a,x2=b,out= re).execute()
    # to 0 -255 
    ten.multiply(x1= re,x2= 255,out= re).execute()

    return re


# Screen

def CScreen(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    ten.subtract(x1= a1,x2= 1,out= a1).execute()

    ten.abs(x= a1,out= a1).execute()

    ten.subtract(x1= b1,x2= 1,out= b1).execute()

    ten.abs(x= b1,out= b1).execute()

    ten.multiply(x1= a1,x2= b1,out= re).execute()

    ten.subtract(x1= re,x2= 1,out= re).execute()

    ten.abs(x= re,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()

    return re


# ColorDodge
def CColorDodge(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    ten.subtract(x1= b,x2= 1,out= b1).execute()

    ten.abs(x= b1,out= b1).execute()
    
    # if b1 == 0 need avoid this form happening
    ten.add(x1= b1,x2= 0.0001,out= b1).execute() 

    ten.true_divide(x1= a1,x2= b1,out= re).execute()

    tem = ten.full(shape= re.shape,fill_value= False,gpu=True)

    ten.less_equal(x1= re,x2= 1,out=tem).execute()
    
    re2 = ten.full(shape= re.shape,fill_value= 1,gpu= True)
    re2.execute()

    ten.take(a= re,indices= tem,out= re2).execute()

    ten.multiply(x1= re2,x2= 255,out= re).execute()

    return re2


# ColorBurn
def CColorBurn(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    ten.subtract(x1= a,x2= 1,out= a1).execute()

    ten.abs(x= a1,out= a1).execute()

    # if b1 == 0 need avoid this form happening
    ten.add(x1= a1,x2= 0.0001,out= a1).execute() 

    ten.true_divide(x1= a1,x2= b1,out= re).execute()

    tem = ten.full(shape= re.shape,fill_value= False,gpu=True)

    ten.less_equal(x1= re,x2= 1,out=tem).execute()
    
    re2 = ten.full(shape= re.shape,fill_value= 1,gpu= True)
    re2.execute()

    ten.take(a= re,indices= tem,out= re2).execute()

    ten.subtract(x1= re2,x2= 1,out= re).execute()

    ten.abs(x= re2,out= re2).execute()

    ten.multiply(x1= re2,x2= 255,out= re).execute()

    return re2

# LinearDodge
def CLinearDodge(a :ten.Tensor,b :ten.Tensor):

   re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
   re.execute()  

   ten.add(x1= a,x2= b,out=re).execute()
   return re
   ...


# LinearBurn
def CLinearBurn(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    ten.add(x1= a1,x2= b1,out= re).execute()

    ten.subtract(x1= re, x2= 1,out= re).execute()

    tem = ten.full(shape= re.shape,fill_value= False,gpu=True)
    tem.execute()

    ten.greater_equal(x1= re,x2= 0,out=tem).execute()
    
    re2 = ten.full(shape= re.shape,fill_value= 0,gpu= True)
    re2.execute()

    ten.take(a= re,indices= tem,out= re2).execute()

    ten.multiply(x1= re2,x2= 255,out= re).execute()

    return re2

# Overlay
def COverlay(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    less = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    less.execute()
    lessTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    lessTen.execute()

    ten.less_equal(x1= a1,x2= 0.50,out=lessTen).execute()

    ten.take(a= a1,indices= lessTen,out= less).execute()

    ten.multiply(x1= less,x2= b1,out= less).execute()
    ten.multiply(x1= less,x2= 2,out= less).execute()

    more = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    more.execute()
    moreTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    moreTen.execute()

    ten.greater(x1= a1,x2= 0.50,out= moreTen).execute()
    ten.take(a= a1,indices= moreTen,out= more).execute()

    ten.subtract(x1= more,x2= 1,out= more).exevute()
    ten.abs(x= more,out= more).execute()

    more2 = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    more2.execute()
    ten.subtract(x1= b1,x2= 1,out= more2).execute()
    ten.abs(x= more2,out= more2).execute()

    ten.multiply(x1= more,x2= more2,out= more).execute()

    ten.multiply(x1= more,x2= 2,out= more).execute()

    ten.subtract(x1= more,x2= 1,out= more).execute()

    ten.abs(x= more,out= more).execute()

    ten.take(a= less,indices= lessTen,out= re).execute()

    ten.take(a= more,indices= moreTen,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()


    return re


# Hard Light
def CHardLight(a :ten.Tensor,b :ten.Tensor):
   
  return COverlay(a= b,b =a)


# Soft light
def CSoftLight(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    less = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    less.execute()
    lessTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    lessTen.execute()
    ten.less_equal(x1= b1,x2= 0.50,out=lessTen).execute()
    ten.take(a= b1,indices= lessTen,out= less).execute()

    ten.subtract(x1= a1,x2= 1,out= less).execute()
    ten.abs(x= less,out=less).execute()

    ten.multiply(x1= less,x2= a1).execute()
    ten.multiply(x1= less,x2= b1).exevute()

    ten.multiply(x1= less,x2= 2).execute()

    tem = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem.execute()
    ten.square(x= a1,out= tem).execute()

    ten.add(x1= less,x2= tem, out= less).execute()


    more = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    more.execute()
    moreTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    moreTen.execute()
    ten.greater(x1= b1,x2= 0.50,out= moreTen).execute()
    ten.take(a= b1,indices= moreTen,out= more).execute()

    ten.subtract(x1= b1,x2= 1,out= more).execute()
    ten.abs(x= more, out= more).execute()

    ten.multiply(x1= more,x2= a1,out=more).execute()
    ten.multiply(x1= more, x2= 2,out= more).execute()

    tem2 = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem2.execute()
    ten.multiply(x1= b1,x2=2,out= tem2).execute()
    ten.subtract(x1= tem,x2= 1,out= tem2).execute()

    tem3 = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem3.execute()
    ten.sqrt(x= a1,out= tem3).execute()

    ten.multiply(x1=tem3,x2= tem2,out= tem2).execute()

    ten.add(x1= more,x2= tem2,out= more).execute()


    ten.take(a= less,indices= lessTen,out= re).execute()

    ten.take(a= more,indices= moreTen,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()


# VividLight
def CVividLight(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    less = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    less.execute()
    lessTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    lessTen.execute()
    ten.less_equal(x1= b1,x2= 0.50,out=lessTen).execute()
    ten.take(a= b1,indices= lessTen,out= less).execute()


    ten.subtract(x1= a1,x2= 1,out=less).execute()
    tem = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem.execute()

    ten.multiply(x1= b1,x2= 2,out=tem).execute()
    ten.true_divide(x1= less,x2= tem,out= less).execute()

    ten.add(x1= less,x2= 1,out= less).execute()

    more = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    more.execute()
    moreTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    moreTen.execute()
    ten.greater(x1= b1,x2= 0.50,out= moreTen).execute()
    ten.take(a= b1,indices= moreTen,out= more).execute()

    tem2 = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem2.execute()

    ten.subtract(x1= b1,x2= 1,out= tem2).execute()
    ten.abs(x= tem2,out= tem2).execute()
     
    ten.multiply(x1= tem2,x2= 2,out= tem2).execute()
      
    ten.true_divide(x1= a1,x2= tem2,out= more).execute()


    ten.take(a= less,indices= lessTen,out= re).execute()

    ten.take(a= more,indices= moreTen,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()

# LinearLight
def CLinearLight(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    
    ten.multiply(x1= b1,x2= 2,out= re).execute()

    ten.add(x1= re,x2= a1,out= re).execute()

    ten.subtract(x1= re,x2= 1,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()

    return re



# Pin Light
def CPinLight(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    less = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    less.execute()
    lessTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    lessTen.execute()
    ten.less_equal(x1= b1,x2= 0.50,out=lessTen).execute()
    ten.take(a= b1,indices= lessTen,out= less).execute()

    ten.multiply(x1= b1,x2= 2,out= less).execute()

    ten.less_equal(x1= a1,x2= less,out= lessTen).execute()

    ten.take(a= a1,indices= lessTen,out= less).execute()
   

    more = ten.zeros(shape= re.shape,dtype= np.float32,gpu= True)
    more.execute()
    moreTen = ten.full(shape= re.shape,fill_value= False,gpu= True)
    moreTen.execute()
    ten.greater(x1= b1,x2= 0.50,out= moreTen).execute()
    ten.take(a= b1,indices= moreTen,out= more).execute()

    ten.subtract(x1= b1,x2= 0.50,out= more).execute()
    ten.multiply(x1= more,x2= 2,out= more).execute()

    ten.greater_equal(x1= a1,x2= more,out=moreTen).execute()
    
    ten.take(a= a1,indices= moreTen,out= more).execute()


    ten.take(a= less,indices= lessTen,out= re).execute()

    ten.take(a= more,indices= moreTen,out= re).execute()

    ten.multiply(x1= re,x2= 255,out= re).execute()

# HardMix
def CHardMix(a :ten.Tensor,b :ten.Tensor):
    
    re = ten.full(shape= a.shape,fill_value= 1.0,dtype= np.float32,gpu= True)
    re.execute()  
 
    # (0 - 255) -> (0,1)
    a1 = ten.zeros(shape= a.shape,dtype= np.float32,gpu=True)
    a1.execute()
    ten.true_divide(x1= a,x2= 255,out= a1).execute() 

    b1 = ten.zeros(shape= b.shape,dtype= np.float32,gpu=True)
    b1.execute()
    ten.true_divide(x1= b,x2= 255,out= b1).execute()

    tem = ten.zeros(shape= a1.shape,dtype= np.float32,gpu=True)
    tem.execute()
    tem2 = ten.full(shape= a.shape,fill_value= False,gpu= True)
    tem2.execute()

    ten.add(x1= a1,x2= b1,out= tem).execute()

    ten.less(x1= tem,x2= 1,out= tem2).execute()

    ten.take(a= tem,indices= tem2,out= re).execute()


    ten.multiply(x1= re,x2= 255,out= re).execute()

    return re

#-------------------------------------------------------------#














## -------------------------------------------------------

##         AMD          ##









##----------------------------------------------------------