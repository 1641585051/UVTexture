from email.mime import image

from mars.tensor.datasource.array import asarray
from .. import cv2
from .. import numpy as np
from ..PIL import Image as image


    


def scaleImage(array : np.ndarray,old_wdith: int,old_height: int,new_width: int,new_height :int):
    
    newarr = np.split(ary= array,indices_or_sections=[3,1],axis=2)
    # split rgb and alpha 

    rgbArr = np.array(object= newarr[0],dtype=np.uint8)

    imag = image.fromarray(rgbArr)

    alphaArr = np.array(object= [newarr[1],newarr[1],newarr[1]],dtype= np.uint8)
     
    alphaImag = image.fromarray(alphaArr) 

    valueType : int = cv2.INTER_AREA

    if old_wdith < new_width and old_height < new_height:
        valueType = cv2.INTER_CUBIC

    elif old_wdith < new_width or old_height < new_height:
        valueType = cv2.INTER_CUBIC
    elif old_wdith > new_width and old_height > new_height: 
        valueType = cv2.INTER_AREA
    elif old_wdith > new_width or old_height > new_height:  
        valueType = cv2.INTER_CUBIC

    imag = cv2.resize(imag,(new_height,new_width),interpolation=valueType)

    alphaImag = cv2.resize(alphaImag,(new_height,new_width),interpolation=valueType)

    rGBEnd  = np.asarray(imag)

    alphaEnd = np.asarray(alphaImag)

    return np.vstack((rGBEnd,alphaEnd))
    
    