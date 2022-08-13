
from types import TracebackType
from ..lookMouse import lookMouse
import datetime


def uvTextureExehook(excepType : type[BaseException], exception: BaseException, other:  TracebackType | None):
   
    lookMouse.unlookMouse()
    print(str(excepType) +"\n" + str(exception) + "\n" + str(other) + "\n" + str(datetime.datetime.now()))

