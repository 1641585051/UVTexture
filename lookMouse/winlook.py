from ctypes import*
import ctypes

#windows
user32 = ctypes.windll.LoadLibrary("user32.dll")

def lookMouse():

  user32.BlockInput(True)




def unlookMouse():
  
  user32.BlockInput(False)

#---
