
from ast import Store
import math

import mathutils

import numpy as np
import taichi as ti
import mars.tensor as ten


from .UVListLayer import BlendMode, BlurType, Stroke

##       CUDA         ##

#------------------------blendMode----------------------------#

# a down layer, b is up layer
# some func don't use alpha 
# a b shape = (m,n,3)




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


# Difference
def CDifference(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
    
    ten.subtract(x1= a,x2= b,out= re).execute()

    ten.abs(x= re,out= re).execute()

    return re


# Exclusion
def CExclusion(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  

    ten.multiply(x1= a,x2= b,out= re).execute()
    ten.multiply(x1= re,x2= -2,out= re).execute()

    ten.add(x1= re,x2= a,out= re).execute()
    ten.add(x1= re,x2= b,out= re).execute()

    return re


# Subtract
def CSubtract(a :ten.Tensor,b :ten.Tensor):
   
    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  
 
    ten.subtract(x1= a,x2= b,out= re).execute()

    return re 


# Divide
def CDivide(a :ten.Tensor,b :ten.Tensor):

    re = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    re.execute()  

    ten.true_divide(x1= a,x2= b,out= re).execute()

    return re


mixmodeFuncs = {

   BlendMode.Normal : CNormal, #0
   
   BlendMode.Darken : CDarken, #1

   BlendMode.Lighten : CLighten, #2

   BlendMode.Multiply : CMultiply, #3
 
   BlendMode.Screen : CScreen, #4

   BlendMode.ColorDodge : CColorDodge, #5
 
   BlendMode.ColorBurn : CColorBurn, #6

   BlendMode.LinearDodge : CLinearDodge, #7

   BlendMode.LinearBurn : CLinearBurn, #8

   BlendMode.Overlay : COverlay, #9

   BlendMode.HardLight : CHardLight, #10

   BlendMode.SoftLight : CSoftLight, #11

   BlendMode.VividLight : CVividLight, #12

   BlendMode.LinearLight : CLinearLight, #13

   BlendMode.PinLight : CPinLight, #14

   BlendMode.HardMix : CHardMix, #15

   BlendMode.Difference : CDifference, #16

   BlendMode.Exclusion : CExclusion, #17

   BlendMode.Subtract : CSubtract, #18

   BlendMode.Divide : CDivide #19

   # Deep,Shallow,Hue,Saturation,Color,Brightness
   # these are not intended to be achieved
   # there are two reasons for this 
   # 1). Deep and Shallow requires merging the channels of the picture,
   # which is not in line with our GPU computing philosophy
   # 2). Hue,Saturation,Color and Brightness uses the HSB color space,
   # whitch is not compatible with the wider RGB color space we expect to
   # use ,and to avoid conversion, does not use the HSB-related algorithm 
   # from Photoshop 



}

#-------------------------------------------------------------#
#-------------------------BlurMode----------------------------#

# func don't use alpha 
# a shape = (m,n,3)



def Null(a : ten.Tensor):

    return a


# this idea form https://blog.ivank.net/fastest-gaussian-blur.html       
# Use multiple mean blur to approximate Gaussian blur
# The copyright is owned by the blogger and I localize it by taichi 

def boxesForGauss(sigma, n):  # standard deviation, number of boxes

    wIdeal = ti.sqrt((12*sigma*sigma/n)+1);  # Ideal averaging filter width 
    wl = math.floor(wIdeal)
    if(wl%2==0): 
       wl = wl - 1
    wu = wl+2
				
    mIdeal = (12*sigma*sigma - n*wl*wl - 4*n*wl - 3*n)/(-4*wl - 4)
    m = ti.round(mIdeal)
    # var sigmaActual = Math.sqrt( (m*wl*wl + (n-m)*wu*wu - n)/12 );
				
    sizes = list()
     
    for i in range(n):

        if i < m:
          sizes.append(wl)
        else:
          sizes.append(wu)  

    return sizes


# Gaussian
def CGaussian(a : ten.Tensor,r :np.float32):


    maskBool = ten.full(shape= a.shape,fill_value= False,gpu= True)
    maskBool.execute()

    maskValue = ten.full(shape= a.shape,fill_value= -1.0,dtype= np.float32,gpu= True) 
    maskValue.execute()

    ten.equal(x1= a,x2= -1.0,out= maskBool).execute()


    channels : list[ten.Tensor] = ten.dsplit(a= a,indices_or_sections= 3)
    channels.execute()

    ndarrs = list(channel.to_numpy() for channel in channels)

    ndarrs = np.array(object= ndarrs,dtype= np.float32)

    ndarrs = ndarrs.reshape(shape=(3,1,a.shape[0],a.shape[1]))

    field :ti.MatrixField = ti.Matrix.field(n = a.shape[1],m= a.shape[0],dtype=np.float32,shape= (3,1))
   
    field.from_numpy(ndarrs)

    targetField : ti.MatrixField = ti.Matrix.field(n = a.shape[1],m= a.shape[0],dtype=np.float32,shape= (3,1))

    
    # Due to the use of GPU ,it will be arithmetic 4 times
    grs = boxesForGauss(r,4) 
   
# taichi #   

    @ti.func
    def getTrueAppendIndex(i,m,appendNum):

        tem = i[0] + appendNum

        if tem > m - 1 :
           k = appendNum % m
           y = (appendNum - k) / m 
           i = (i[0] + k,i[1] + y)
        elif tem == m - 1:
           i = (tem,i[1])
        else:  
           i = (i[0] + appendNum,i[1])

        return i

    @ti.kernel
    def copy():
       for ind in ti.grouped(field):
           for xy in ti.grouped(ti.ndrange(field.m,field.n)):
               targetField[ind][xy] = field[ind][xy]

    @ti.kernel
    def blursH(m,n,r,iarr,ch):
        for i in ti.ndrange(n,1):
            a = (m,i[0])
            li = a 
            ri = getTrueAppendIndex(a,m,r)
            fv = field[ch][a]
            lv = field[ch][getTrueAppendIndex(a,m,m-1)]
            val = (r+1)*fv
            for j in ti.ndrange(r,1):
                 c = getTrueAppendIndex(a,m,j[0])
                 val += field[ch][c]

            for j in ti.ndrange(r + 1,1):
               ri = getTrueAppendIndex(ri,m,1)
               val += (field[ch][ri] - fv) 
               a = getTrueAppendIndex(a,m,1)
               targetField[ch][a] = ti.round(val*iarr)
            
            for j in ti.ndrange(m-2*r-1,1):

               ri = getTrueAppendIndex(ri,m,1)
               li = getTrueAppendIndex(li,m,1)
               val += (field[ch][ri] - field[ch][li])
               a = getTrueAppendIndex(a,m,1)
               targetField[ch][a] = ti.round(val*iarr)

            for j in ti.ndrange(r,1):

                li = getTrueAppendIndex(li,m,1)
                val += (lv  - field[ch][li])
                a = getTrueAppendIndex(a,m,1)
                targetField[ch][a] = ti.round(val*iarr)
    

    @ti.kernel
    def blursW(m,n,r,iarr,ch):
        for i in ti.ndrange(m,1):
            a = (i[0],n)
            li = a 
            ri = getTrueAppendIndex(a,m,r * m)
            fv = field[ch][a]
            lv = field[ch][getTrueAppendIndex(a,m,m*(n -1))]
            val = (r+1)*fv
            for j in ti.ndrange(r,1):
                 c = getTrueAppendIndex(a,m,j[0] * m)
                 val += field[ch][c]

            for j in ti.ndrange(r + 1,1):
               
               val += (field[ch][ri] - fv) 
               
               targetField[ch][a] = ti.round(val*iarr)
            
               ri = getTrueAppendIndex(ri,m,m)
               a = getTrueAppendIndex(a,m,m)
              
            for j in ti.ndrange(n-2*r-1,1):
             
               val += (field[ch][ri] - field[ch][li])
               a = getTrueAppendIndex(a,m,1)
               targetField[ch][a] = ti.round(val*iarr)
               
               li = getTrueAppendIndex(li,m,m)
               ri = getTrueAppendIndex(ri,m,m)
               a = getTrueAppendIndex(a,m,m)

            for j in ti.ndrange(r,1):
                
                val += (lv  - field[ch][li])
                
                targetField[ch][a] = ti.round(val*iarr)
     
                li = getTrueAppendIndex(li,m,m)
                a = getTrueAppendIndex(a,m,m)


# taichi # 

    copy()

    for i in range(5):
         
       r= (grs[i] - 1) /2
       for ch in ti.ndrange(3,1): # channel rgb 3
          blursH(m= field.m,n= field.n,r = r,iarr= 1 / (r+r+1),ch = ch[0]) 
          blursW(m= field.m,n= field.n,r = r,iarr= 1 / (r+r+1),ch = ch[0])  

    re = ten.tensor(data= targetField.to_numpy().reshape(a.shape),gpu= True)
    re.execute()

    ten.take(a= maskValue, indices= maskBool,out=re).execute()

    return re 




# the func idea from https://blog.demofox.org/2015/08/18/box-blur/
# The copyright is owned by the blogger and I localize it by taichi 

# Box
def CBoxBlur(a : ten.Tensor,xblur : np.uint16,yblur : np.uint16):

    shape = a.shape

    maskBool = ten.full(shape= shape,fill_value= False,gpu= True)
    maskBool.execute()

    maskValue = ten.full(shape= shape,fill_value= -1.0,dtype= np.float32,gpu= True) 
    maskValue.execute()

    ten.equal(x1= a,x2= -1.0,out= maskBool).execute()

    channels = ten.dsplit(a= a,indices_or_sections= 3)
    channels.execute()

    ndarrs = list(channel.to_numpy() for channel in channels)

    ndarrs = np.array(object= ndarrs,dtype= np.float32)

    ndarrs = ndarrs.reshape(shape=(3,1,shape[0],shape[1]))

    field :ti.MatrixField = ti.Matrix.field(n = shape[1],m= shape[0],dtype=np.float32,shape= (3,1))
   
    field.from_numpy(ndarrs)

    targetField : ti.MatrixField = ti.Matrix.field(n = a.shape[1],m= a.shape[0],dtype=np.float32,shape= (3,1))

    @ti.kernel
    def copy():
       for ind in ti.grouped(field):
           for xy in ti.grouped(ti.ndrange(field.m,field.n)):
               targetField[ind][xy] = field[ind][xy]

 
    # horizontal blur from srcImage into tmpImage

    @ti.kernel
    def blurHorizontal(f,half,weight,ch):
        for ind in ti.grouped(f):
                
            blurredPixel = 0.0
            for i in ti.ndrange(2 * half + 1,1):
                    
                i -= half  

                pixel = f[ind[0] + i[0],ind[1]]
                blurredPixel += float(pixel) * weight
                        
            targetField[ch][ind] = blurredPixel

                
    # vertical blur from tmpImage into destImage
    
    @ti.kernel
    def blurVertical(f,half,weight,ch):
        for ind in ti.grouped(f):
                
            blurredPixel = 0.0
            for i in ti.ndrange(2 * half + 1,1):
                    
                i -= half    

                pixel = f[ind[0],ind[1] + i[0]]
                blurredPixel += float(pixel) * weight
                        
            targetField[ch][ind] = blurredPixel


    copy()

    for ch in range(3):

       f = field[ch]
    
       weightx = 1.0 / float(xblur)
       halfx = xblur / 2

       weighty = 1.0 / float(yblur)
       halfy = yblur / 2
  
       blurHorizontal(f= f,half= halfx,weight= weightx,ch = ch)
       blurVertical(f= f,half= halfy,weight= weighty,ch= ch)

    re = ten.tensor(data= targetField.to_numpy().reshape(a.shape),gpu= True)
    re.execute()
 
    ten.take(a= maskValue, indices= maskBool,out=re).execute()

    return re



# UNFINISHED #  
#Kawase
def CKawase(a : ten.Tensor):






    return a 




# UNFINISHED #  
# Dual
def CDual(a : ten.Tensor,blur_radius=None):

   
    
    
    return a



blurModes = {

   BlurType.Null : Null,
   BlurType.Gaussian : CGaussian,
   BlurType.Box : CBoxBlur,
   




}






##-----------------------Strock-------------------------------##


# Strock Base
def CStrockBase(a : ten.Tensor,strockweith : int,color : mathutils.Vector):

    maskBool = ten.full(shape= a.shape,fill_value= False,gpu= True)
    maskBool.execute()

    maskValue = ten.full(shape= a.shape,fill_value= -1.0,dtype= np.float32,gpu= True) 
    maskValue.execute()

    ten.equal(x1= a,x2= -1.0,out= maskBool).execute()

    backTen : ten.Tensor = ten.zeros(shape= a.shape,dtype= np.float32,gpu= True)
    backTen.execute()

    backIndices = ten.full(shape= a.shape,fill_value= False,gpu= True)
    backIndices.execute()
  
    ten.equal(x1 = a,x2= -1.0,out= backIndices).execute()
    # -1 is mask value 
    ten.take(a= a, indices= backIndices,out= backTen).execute()

    strockKernel = ti.Vector(arr= [[1,1],
                                   [1,1]],
                             dt= np.float32
                             )

    backNdarr : np.ndarray = backTen.to_numpy()

    backNdarr = backNdarr.reshape(shape= (a.shape[0],a.shape[1],1,3))

    tiBack : ti.MatrixField = ti.Matrix.field(n= 1,m= 3,shape= (a.shape[0],a.shape[1]),dtype= np.float32)

    tiBack.from_numpy(backNdarr)
 
    timap : ti.MatrixField = ti.Matrix.field(n= 5,m= 2,shape= (a.shape[0] - 1,a.shape[1] - 1),dtype= np.float32)
    # [[mapVlaue,        0],
    #  [[0,0][0], [0,0][1]],
    #  [[0,1][0], [0,1][1]],
    #  [[1,0][0], [1,0][1]],
    #  [[1,1][0], [1,1][1]]
    #  ]
    # -----> y (1)
    # |   tiBack [[(0,0),(0,1)],
    # x(0)       [(1,0),(1,1)]]

    @ti.kernel
    def getBackMap():

        for ind in ti.grouped(timap):

            backind = ti.Vector([[ind                ,[ind[0],ind[1] + 1]],
                       [[ind[0] + 1,ind[1]],[ind[0] + 1,ind[1] + 1]]
                      ])

            data = ti.Vector([[tiBack[backind[0,0]][0,0],tiBack[backind[0,1]][0,0]],
                    [tiBack[backind[1,0]][0,0],tiBack[backind[1,1]][0,0]]
                   ])       
                     
            data = strockKernel * data   

            mapvalue = (data[0,0] + data[0,1] + data[1,0] + data[1,1]) / 4

            timap[ind][0,0] = mapvalue
            timap[ind][0,1] = 0  

            timap[ind][1,0] = backind[0,0][0] 
            timap[ind][1,1] = backind[0,0][1] 

            timap[ind][2,0] = backind[1,0][0] 
            timap[ind][2,1] = backind[1,0][1] 

            timap[ind][3,0] = backind[0,1][0] 
            timap[ind][3,1] = backind[0,1][1] 

            timap[ind][4,0] = backind[1,1][0] 
            timap[ind][4,1] = backind[1,1][1] 
 

       
    getBackMap()

    @ti.func
    def MakeSureDir(d00,d01,d10,d11):

       # the orientation is defined as standard by array

       # ([[d00,d01],
       #   [d10,d11]
       #   ])

        dirc = ti.Vector([0,0])

        if d11 - d00 > 0:
           dirc = dirc * ti.Vector([1,1])
        elif d11 - d00 < 0: 
           dirc = ti.Vector([-1,-1])
        

        if d01 - d10 > 0: 
           dirc = dirc * ti.Vector([-1,1])
        elif d01 - d10 < 0:
           dirc = dirc * ti.Vector([1,-1])

        return dirc


    @ti.func
    def updateBack(x_ind,y_ind,count):
        
        x = x_ind
        y = y_ind

        ofset = ti.Vector([0,0])          

        for i in ti.ndrange((0,count)):
             
            x = x + ofset[0]
            y = y + ofset[1]

            checkIndex = ti.Vector([[[x - 1,y + 1],[x + 1,y + 1]],
                                    [[x - 1,y - 1],[x + 1,y - 1]]
                                    ])

            dir = ti.Vector([[0,0],
                             [0,0]
                             ])

            for ind in ti.grouped(checkIndex):

                if tiBack[checkIndex[ind]][0,0] == 0:
                            
                    d = checkIndex[ind]
                            
                    dir[ind] = 1

                    drawIndex = ti.Vector([[[d[0] - 1,d[1] + 1],[d[0],d[1] + 1],[d[0] + 1,d[1] + 1]],
                                            [[d[0] - 1,d[1]],    d,             [d[0] + 1,d[1]]],
                                            [[d[0] - 1,d[1] - 1],[d[0],d[1] - 1],[d[0] + 1,d[1] - 1]]
                                            ])

                    for drawInd in ti.grouped(drawIndex):

                        tiBack[drawIndex[drawInd]] = ti.Vector([1,1,1])
                        
                    
            temofset = MakeSureDir(dir[0,0],dir[0,1],dir[1,0],dir[1,1])
            if temofset != ti.Vector([0,0]):
                ofset = temofset
            
            
    @ti.kernel
    def strock(weith):
        
        for ind in ti.grouped(timap):

            if timap[ind][0,0] > -1 and timap[ind][0,0] < 0 :

              if tiBack[timap[ind][1,0],timap[ind][1,1]] == 0: 
              
                 updateBack(x= timap[ind][1,0],y= timap[ind][1,1],count= weith)
              
              if tiBack[timap[ind][2,0],timap[ind][2,1]] == 0:
              
                 updateBack(x= timap[ind][2,0],y= timap[ind][2,1],count= weith)
              
              if tiBack[timap[ind][3,0],timap[ind][3,1]] == 0:

                 updateBack(x= timap[ind][3,0],y= timap[ind][3,1],count= weith)
              
              if tiBack[timap[ind][4,0],timap[ind][4,1]] == 0: 
                
                 updateBack(x= timap[ind][4,0],y= timap[ind][4,1],count= weith)
            


    strock(weith= strockweith)

    renumpy = tiBack.to_numpy()
    
    oneTen = ten.tensor(data= renumpy,dtype= np.float32,gpu=True)
    oneTen.execute()
    
    drawBools = ten.full(shape= a.shape,fill_value= False,gpu= True)
    drawBools.execute()

    ten.equal(x1= oneTen,x2= -1,out= drawBools).execute()

    zeros = ten.full(shape= a.shape,fill_value= 0,gpu= True)

    ten.take(a= zeros,indices= drawBools,out= oneTen).execute()

    drawBools = ten.full(shape= a.shape,fill_value= False,gpu= True)
    drawBools.execute()

    re = ten.tensor(data= a.to_numpy(),dtype= np.float32,gpu=True)
    re.execute()

    ten.equal(x1= oneTen,x2= 1,out= drawBools).execute()

    xyz = color.xyz

    ten.multiply(x1= oneTen,x2= [[[xyz[0],xyz[1],xyz[2]]]],out= oneTen).execute()

    ten.take(a= oneTen,indices= drawBools,out= re).execute()

    re = CGaussian(re,strockweith / 2)
    maskImg = re.to_numpy()

    from skimage.filters import _unsharp_mask as mask
    maskImg = mask.unsharp_mask(image =maskImg)

    re = ten.tensor(data= maskImg,dtype= np.float32,gpu=True)
    re.execute()

    ten.take(a= maskValue, indices= maskBool,out=re).execute()

    return re


storks = {

   Stroke.Base : CStrockBase,


}


# the func idea form https://blog.csdn.net/weixin_45116749/article/details/119644866


#imageScaling 
def CImageScaling(a : ten.Tensor,new_width :int,new_height : int ):

    src = ti.Vector(data= a.to_numpy(),dtype= np.float32)

    
    src_rows = a.shape[0]
    src_cols = a.shape[1]
    deep = a.shape[2]

    x = 1.0 / (1.0* src_rows / new_width)
    y = 1.0 / (1.0* src_cols/ new_height)

    dst_cols : int = ti.round(src_cols * x)  #width
    dst_rows : int = ti.round(src_rows * y)  #把一个小数四舍五入 height
	
    tem = np.ndarray(shape= (dst_rows,dst_cols,deep),dtype= np.float32)

    dst = ti.Vector(arr= tem,dt= np.float32)

    @ti.kernel
    def bilinera():
        #for (int i = 0; i < dst.rows; i++):
        for i in ti.ndrange((0,dst_rows)):
            #几何中心对齐
            index_i = (i + 0.5) / y - 0.5
            #防止越界
            if (index_i < 0):
               index_i = 0
            if (index_i >= src_rows - 1):
               index_i = src_rows - 2
            #相邻2*2像素的行（坐标）
            i1 = ti.floor(index_i) # 把一个小数向下取整 2.2==2
            i2 = ti.ceil(index_i) # 把一个小数向上取整  2.2==3
            #u为得到浮点型坐标行的小数部分
            u = index_i - i1
            #for (int j = 0; j < dst.cols; j++)
            for j in ti.ndrange((0,dst_cols)):
                #几何中心对齐
                index_j = (j + 0.5) / x - 0.5
                #防止越界
                if (index_j < 0):
                   index_j = 0
                if (index_j >= src_cols - 1):
                   index_j = src_cols - 2
                #相邻2*2像素的列（坐标）
                j1 = ti.floor(index_j)
                j2 = ti.ceil(index_j)
                #v为得到浮点型坐标列的小数部分
                v = index_j - j1
                
                if deep == 3:
                    #彩色图像
                    dst[i, j][0] = (1 - u)*(1 - v)*src[i1,j1][0] + (1 - u)*v*src[i1,j2][0] + u*(1 - v)*src[i2,j1][0] + u*v*src[i2,j2][0]
                    dst[i, j][1] = (1 - u)*(1 - v)*src[i1,j1][1] + (1 - u)*v*src[i1,j2][1] + u*(1 - v)*src[i2,j1][1] + u*v*src[i2,j2][1]
                    dst[i, j][2] = (1 - u)*(1 - v)*src[i1,j1][2] + (1 - u)*v*src[i1,j2][2] + u*(1 - v)*src[i2,j1][2] + u*v*src[i2,j2][2]
                    
                else:
                    for d in ti.ndrange((0,deep)):
                        dst[i, j][d] = (1 - u)*(1 - v)*src[i1,j1][d] + (1 - u)*v*src[i1,j2][d] + u*(1 - v)*src[i2,j1][d] + u*v*src[i2,j2][d]


    bilinera()        
	
    redata = dst.to_numpy()
    re = ten.tensor(data= redata,dtype= np.float32,gpu= True)
    re.execute()

    return re

   

#expend all effect funcs 
all_effect_funcs = blurModes | storks    # | ....


#-------------------------------------------------------------#






## -------------------------------------------------------

##         AMD          ##









##----------------------------------------------------------