import bpy
import bmesh as mesh
import mathutils

def singularFaceJudgment(face : mesh.bmesh.types.BMFace):
    '''if face have point not in face return true'''

    verts = face.verts
    count = verts.count()
    if count > 4:
       return True
    elif count == 4 :
       v0 = verts[0].co
       v1 = verts[1].co
       v2 = verts[2].co 
       v3 = verts[3].co
 
       t0 : mathutils.Vector = v1 - v0 
       t0.normalize()

       t1 : mathutils.Vector = v2 - v1
       t1.normalize()

       t2 : mathutils.Vector = v3 - v2
       t2.normalize()

       t3 : mathutils.Vector = v0 - v3
       t3.normalize()

       if ((t0.cross(t1) == t1.cross(t2) or t0.cross(t1) + t1.cross(t2) == 0) and
           (t1.cross(t2) == t2.cross(t3) or t1.cross(t2) + t2.cross(t3) == 0) and
           (t2.cross(t3) == t3.cross(t0) or t2.cross(t3) + t3.cross(t0) == 0) and
           (t3.cross(t0) == t0.cross(t1) or t3.cross(t0) + t0.cross(t3) == 0)
          ):
          return False
       else:
          return True    


    elif count == 3:
        return False



