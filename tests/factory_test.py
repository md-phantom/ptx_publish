from ..app_modules.maya import ptx_maya_publish as pmp
#from ..app_modules.blender import ptx_blender_publish as pbp

def main():
    mdl_asset_info = [ 'muks', 'hero', 'mdl', 'v001', 'root', ['geom1', 'geom2', 'geom3', 'geom4']]
    luk_asset_info = [ 'muks', 'hero', 'mdl', 'v001', [
                                                        ['shader1', 
                                                         [
                                                             ['attr1', 'val'], 
                                                             ['attr2', 5.0], 
                                                             ['attr3', 'texpath']
                                                         ], 
                                                         ['face1', 'face2', 'face3']
                                                        ],
                                                        ['shader2', 
                                                         [
                                                             ['attr1', 2.0], 
                                                             ['attr2', 50.0], 
                                                             ['attr3', 'texpath']
                                                         ], 
                                                         ['obj1']
                                                        ]
                                                      ]]

    maya_mdlp = pmp.factory.create('MAYA', 'MDLP', *mdl_asset_info)
    maya_mdlp.publish()
    print(maya_mdlp.asset.geom_list)

    maya_lukp = pmp.factory.create('MAYA', 'LUKP', *luk_asset_info)
    print(maya_lukp.asset.shader_assignment[0].shader_name)
    maya_lukp.publish()

    #blender_mdlp = pbp.factory.create('BLENDER', 'MDLP', **asset_info)
    #blender_mdlp.publish()
    #print(blender_mdlp.asset.asset_name)