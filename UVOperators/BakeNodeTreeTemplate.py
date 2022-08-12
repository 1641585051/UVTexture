
import operator

import bpy

from ..dataDefine import UVListLayer




def findTemplateFunc(bl_enum :str):
    '''bl_num is BakeTemplate enumProperty'''
    for key in funcs.keys():
        if operator.contains(bl_enum,str(key)):
            return funcs[key]

    

def BakeNodeTreeTemplate0(object : bpy.types.Object,image : bpy.types.Image,propertyData : bpy.types.CollectionProperty,dataIndex : int):
    '''this func use ShaderNodeMixShader,
                     ShaderNodeEmisson,
                     ShaderNideBSDFDiffuse 
                     and ShaderNodeTexImage
                     
       as base bake node tree, we only use Emisson and color,
       and bake type only have emisson 
                     
       color and strengh is NodeSocket in ShaderNodeEmisson  

       propertyData need Data name : color, strengh  

                
                     '''
   
    usingShaderNodeNames = ('ShaderNodeMixShader','ShaderNodeEmisson','ShaderNideBSDFDiffuse','ShaderNodeTexImage') 

    MaterialTemplate0Name = "uv_texture_material0" + object.name

    def getNodeInNodeTreeDict(nodeTree : bpy.types.NodeTree) -> bpy.types.Node:
        
       items = ((node.bl_idname,node) for node in nodeTree.nodes.values())
        
       return dict(items) 

    

    solts = object.material_slots

    material : bpy.types.Material = None

    if MaterialTemplate0Name not in bpy.data.materials.keys():

        material = bpy.data.materials.new(MaterialTemplate0Name)
        if material not in bpy.data.materials.values():
           bpy.data.materials.append(material)


    if MaterialTemplate0Name not in solts.keys():
        
        solts.append(bpy.data.materials[MaterialTemplate0Name])
    

    material = solts[solts.find(MaterialTemplate0Name)]
    
    material.use_nodes = True

    nodeTree = material.node_tree

    nodes = nodeTree.nodes
    
    NodeIdNamedic = getNodeInNodeTreeDict()

    output : bpy.types.Node = None

    templateIdNames = [node.bl_idname for node in nodes.values()]

    output : bpy.types.Node = None
    if 'ShaderNodeOutputMaterial' not in templateIdNames:
        output = nodes.new(type='ShaderNodeOutputMaterial')
    else:
        output = NodeIdNamedic['ShaderNodeOutputMaterial']

    # delete default ShaderNodeBsdfPrincipled shaderNode
    if 'ShaderNodeBsdfPrincipled' in templateIdNames:
        bsdfpr = nodes[nodes.find('ShaderNodeBsdfPrincipled')]
        
        nodes.remove(bsdfpr)

    mix : bpy.types.Node = None
    mix_outputSocket = None
    mix_inputSocket = None

    if 'ShaderNodeMixShader' not in templateIdNames:
        
        mix = nodes.new(type='ShaderNodeMixShader')    

        output_InputSocket = output.inputs
        mix_outputSocket = mix.outputs
        mix_inputSocket = mix.inputs

        nodeTree.links.new(input= mix_outputSocket[0],output= output_InputSocket[0]) # ShaderNodeMixShader : shader -> ShaderNodeOutputMaterial : surface
    else:
        mix = NodeIdNamedic['ShaderNodeMixShader']
        mix_outputSocket = mix.outputs
        mix_inputSocket = mix.inputs



    emisson : bpy.types.ShaderNodeEmission = None
    emisson_outputSocket = None
    emisson_inputSocket = None

    if 'ShaderNodeEmisson' not in templateIdNames: 
        
        emisson = nodes.new('ShaderNodeEmisson')
        
        emisson_outputSocket = emisson.outputs
        emisson_inputSocket = emisson.inputs

        nodeTree.links.new(input= emisson_outputSocket[0],output= mix_inputSocket[1]) # ShaderNodeEmisson : Emisson -> ShaderNodeMixShader : shader (0)
    
    else:

        emisson = NodeIdNamedic['ShaderNodeEmisson']
        emisson_outputSocket = emisson.outputs
        emisson_inputSocket = emisson.inputs

    
    color : tuple[float,float,float] = propertyData[dataIndex].color
    listColor = list(color)
    listColor.append(1.0)

    emisson_color : bpy.types.NodeSocketColor = emisson_inputSocket[0]
    emisson_color.default_value = listColor

    strengh : float = propertyData[dataIndex].strengh

    emisson_strengh : bpy.types.NodeSocketFloat = emisson_inputSocket[1]
    emisson_strengh.default_value = strengh


    diffuse : bpy.types.ShaderNodeBsdfDiffuse
    diffuse_outputSocket = None
    diffuse_inputSocket = None

    if 'ShaderNodeBSDFDiffuse' not in templateIdNames :

        diffuse = nodes.new(type= 'ShaderNodeBSDFDiffuse')
        
        diffuse_outputSocket = diffuse.outputs
        diffuse_inputSocket = diffuse.inputs
        nodeTree.links.new(input= diffuse_outputSocket[0],output= mix_inputSocket[2]) # ShaderNideBSDFDiffuse : BSDF -> ShaderNodeMixShader : shader (1)
    else:

        diffuse = NodeIdNamedic['ShaderNodeBSDFDiffuse']
        diffuse_outputSocket = diffuse.outputs
        diffuse_inputSocket = diffuse.inputs
       
    tex : bpy.types.ShaderNodeTexImage = None
    tex_outputSocket = None

    if 'ShaderNodeTexImage' not in templateIdNames:

        tex : bpy.types.ShaderNodeTexImage = nodes.new(type= 'ShaderNodeTexImage')

        tex_outputSocket = tex.outputs
    
        nodeTree.links.new(input= tex_outputSocket[0],output= diffuse_inputSocket[0]) # ShaderNodeTexImage : Color -> ShaderNideBSDFDiffuse : Color
    else:

        tex = NodeIdNamedic['ShaderNodeTexImage']
        
    tex.image = image

    for idname in templateIdNames:
       if idname not in usingShaderNodeNames:
          nodes.remove(NodeIdNamedic[idname]) 

    









#-------------------------------------------------------------    

funcs = {
    UVListLayer.BakeTemplate.Base : BakeNodeTreeTemplate0,
    


}    
'''all template func in this'''
