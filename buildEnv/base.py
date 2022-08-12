
from genericpath import isfile
import operator
import os 
import json
from shutil import copyfile

# use upgrade value when new blender
blenderVersion = "3.2"


# UVTexture Source dirs
sourceCodeDirNames ={
   
   "__init__.py"
   "buildenv",
   "DataDifine",
   "tools",
   "UI",
   "UVMapping",
   "UVOperators",

   

   

}


otherNoNeedDirs = {
    # windows
    "__pycache__  ",
    "license  ",
    ".git  ",
    ".gitignore  ",
    '.txt  ',
    'README.md',

    #linux
    




    
}




def copy(src :str ,dst :str):
    
    if not os.path.exists(dst):
        os.makedirs(dst)
    if os.path.exists(src):
        for file in os.listdir(src):
            filePath = os.path.join(src,file)
            dstPath = os.path.join(dst,file)
            if os.path.isfile(os.path.join(src,file)):
                copyfile(src=filePath,dst= dstPath)
            else:
                copy(src= filePath, dst= dstPath)




def envDirs(rootpath : str):

    paths = os.listdir(rootpath)
    lm = lambda dirName : dirName if not os.path.isdir(dirName) else None
    tempList = list((lm(dirName= dirName) for dirName in paths)) 
    
    endList = list()
    for ind in range(len(tempList)):
        if (tempList[ind] != None and
             not operator.contains(str(sourceCodeDirNames),tempList[ind]) and
             not operator.contains(str(otherNoNeedDirs),tempList[ind])
                            
             ):
           endList.append(rootpath + tempList[ind])
      
    return endList



def getPackagesDir(exeDir: str):
   
    return os.path.dirname(os.path.dirname(exeDir)) + os.path.sep + "lib" + os.path.sep + "site-packages" + os.path.sep
   
    
blenderRelativePath = "blender" + os.path.sep + blenderVersion + os.path.sep +"python" + os.path.sep + "bin" + "python"

def findBlenderfromJson(jsonFilePath: str):
    
    f = open(jsonFilePath,'r',encoding='utf-8')
    obj = json.load(f)
    path :str = obj["blenderExeDir"]
    if operator.contains(path,blenderRelativePath):
        raise SystemExit(jsonFilePath + ": no found blender python execute file")
        
    if path.find('\\') != -1:
        path.replace('\\',os.path.sep)
    elif path.find('/') != -1:
        path.replace('/',os.path.sep)

    return path
    
    


def getrootPath():

   dir0 = os.path.dirname(os.path.dirname(__file__)) + os.path.sep
   return dir0
   

def copyRun(envDirList : list[str],packDir :str):

    for envDir in envDirList:
        if (not operator.contains(envDir,'.') or
            operator.contains(envDir,'dist-info')):
            
            eles = str(envDir).split(os.path.sep)
            DirName = eles[len(eles) - 1]
            print(DirName + " <<dir>> " + "  copy to [" + packDir + DirName + "]")
            copy(src= envDir,dst= packDir + DirName)

        
        elif ((operator.contains(envDir,'.') or
            operator.contains(envDir,'dist-info')) and 
            os.path.isdir(envDir)
            ):

            eles = str(envDir).split(os.path.sep)
            DirName = eles[len(eles) - 1]
            print(DirName + " <<dir>> " + "  copy to [" + packDir + DirName + "]")
            copy(src= envDir,dst= packDir + DirName)


        else:
            Eles = str(envDir).split(os.path.sep)
            dirName = Eles[len(Eles) - 1]
            print(dirName + "  <<file>>  " + "  copy to [" + packDir + "]") 
            copyfile(src=envDir,dst=packDir + dirName)



def main():
    
    path = getrootPath()

    exedir = findBlenderfromJson(path + "buildenv" + os.path.sep + "env.json")

    envDirList = envDirs(path)

    packDir = getPackagesDir(exeDir= exedir)
    print(packDir + " ..  as target ")

    copyRun(envDirList= envDirList,packDir= packDir)



if __name__ == '__main__':
    main()
         

   



   