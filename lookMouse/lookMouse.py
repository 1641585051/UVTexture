from ast import operator
import sys
import operator


def lookMouse():
    if operator.contains("win32",sys.platform) :
        import winlook
        winlook.lookMouse()
        
    elif operator.contains("linux",sys.platform):
        pass
   


def unlookMouse():
    if operator.contains("win32",sys.platform) :
        import winlook
        winlook.unlookMouse()
    elif operator.contains("linux",sys.platform):
        pass
    