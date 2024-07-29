from pxr import Usd, Sdf, UsdGeom, Kind, Gf, UsdShade
from pathlib import Path

from chitragupta.ptx_data_structs import ptx_usd_structs as ptusds


def usd_stage(pfx_stage_path: Path, stage_up_axis: UsdGeom.Tokens = UsdGeom.Tokens.y) -> Usd.Stage:
    """
    * Take a path, and see if a USD stage exists here.
    * If it exists, just open the stage and return it. If it doesn't, create a new usd stage
    * at that location.
    """
    usd_stage = None
    # Create the payload stage and save it
    if not Path(pfx_stage_path).exists():
        usd_stage = Usd.Stage.CreateNew(pfx_stage_path)
        UsdGeom.SetStageUpAxis(usd_stage, stage_up_axis)
    else:
        usd_stage = Usd.Stage.Open(pfx_stage_path)

    return usd_stage


def usd_root_prim(stage: Usd.Stage, root_prim_name: str, create_xform: bool = True) -> Usd.Prim:
    """
    * See if the stage has a root prim, and if it exists, return it.
    * If it doesn't, then create one, set it as the root and default prim, and return it.
    """
    if stage.GetPrimAtPath(f'/{root_prim_name}'):
        return stage.GetPrimAtPath(f'/{root_prim_name}')
    
    if create_xform:
        root_prim: UsdGeom.Xform = UsdGeom.Xform.Define(stage, Sdf.Path(f'/{root_prim_name}')).GetPrim()
    else:
        root_prim: Usd.Prim = stage.DefinePrim(Sdf.Path(f'/{root_prim_name}'))

    stage.SetDefaultPrim(root_prim)

    return root_prim


def root_asset_info(root_prim: Usd.Prim, asset_path: str, asset_name: str):
    """
    * Adds in the root asset info
    """
    model_api = Usd.ModelAPI(root_prim)
    info = {
        'identifier': Sdf.AssetPath(asset_path), 
        'name': asset_name
    }
    
    model_api.SetAssetInfo(info)


def usd_reference(prim: Usd.Prim, asset_path: str, asset_prim_path: str) -> Sdf.Reference:
    """
    * Search the prim for any reference with the asset_path and prim_path
    * If it exists, return the reference, else, create it and return it.
    """
    usd_ref = None
    if prim.HasAuthoredReferences():
        for prim_spec in prim.GetPrimStack():
            for ref in prim_spec.referenceList.prependedItems:
                if (ref.assetPath == asset_path) and (ref.primPath == asset_prim_path):
                    usd_ref = ref
                    break
            if usd_ref:
                break
    
    if not usd_ref:
        usd_ref = Sdf.Reference(asset_path, asset_prim_path)
        prim.GetReferences().AddReference(usd_ref, Usd.ListPositionFrontOfPrependList)

    return usd_ref


def usd_mesh_payload(stage: Usd.Stage, prim_path: str, extern_payload_path: Path, payload_prim_path: str) -> UsdGeom.Mesh:
    """
    * Get the USD mesh prim with a payload, if it exists.
    * If it doesn't exist, create one.
    """
    if stage.GetPrimAtPath(f'{prim_path}'):
        return stage.GetPrimAtPath(f'{prim_path}')
    
    mesh_payload: UsdGeom.Mesh = UsdGeom.Mesh.Define(stage, prim_path).GetPrim()
    mesh_payload.GetPayloads().AddPayload(
        assetPath = str(extern_payload_path),
        primPath = payload_prim_path
    )
    # add the material binding API
    mesh_payload.ApplyAPI('MaterialBindingAPI')

    return mesh_payload


def usd_scope(stage: Usd.Stage, parent_prim: Usd.Prim = None) -> Usd.Prim:
    """
    * Define a scope in the stage. If we have a valid parent prim, define the scope
    * under the prim, else define it at the root.
    """
    geom_scope: Usd.Prim = stage.DefinePrim(parent_prim.Getpath() if parent_prim else "/", "Scope")
    return geom_scope


def usd_create_mtlx(stage: Usd.Stage, parent_prim: Usd.Prim = None, mtl_name: str = "MtlX") -> UsdShade.Material:
    """
    * Create a mtlx shader and override the parameters that need to be overridden.
    """
    # define the looks scope
    looks_path = Sdf.Path(parent_prim.GetPath().AppendChild("Looks") if parent_prim else "/Looks")
    looks_scope = stage.DefinePrim(looks_path, "Scope")

    # create the material definition from the template mtlx available to us
    mat_path = looks_path.AppendChild(f"{mtl_name}")
    mat_def = UsdShade.Material.Define(stage, mat_path)

    # hardcoding the material class for now; 
    # TODO: figure out where these definitions are, and how to add to these
    inherits = stage.GetPrimAtPath(mat_path).GetInherits()
    inherits.AddInherit(Sdf.Path("/__class_mtl__/mtlxmaterial"))

    # Create the MtlX surface shader definitions
    shd_std_srf = UsdShade.Shader.Define(stage, mat_path.AppendChild("StandardSurface"))
    shd_std_srf.CreateIdAttr("ND_standard_surface_surfaceshader")

    # Create the MtlX displacement shader definitions
    shd_displ = UsdShade.Shader.Define(stage, mat_path.AppendChild("Displacement"))
    shd_displ.CreateIdAttr("ND_displacement_float")

    # Hook up the outputs of these shaders to the outputs on the main material
    mat_def.CreateSurfaceOutput("mtlx").ConnectToSource(shd_std_srf.ConnectableAPI(), "surface")
    mat_def.CreateDisplacementOutput("mtlx").ConnectToSource(shd_displ.ConnectableAPI(), "out")

    return mat_def


def usd_create_texture(stage: Usd.Stage, parent_prim: Usd.Prim, texture_path: str, param_name: str, uv_tile: ptusds.Float2 = ptusds.Float2(1.0, 1.0), mtl_name: str = "MtlX"):
    """
    * Create a UsdUVTexture node
    """
    # define the Textures scope
    tex_scope_path = Sdf.Path(parent_prim.GetPath().AppendChild(f"{mtl_name}Textures"))
    tex_scope = stage.DefinePrim(tex_scope_path, "Scope")

    # Define the UsdUV Texture
    tex_path = tex_scope_path.AppendChild(f"{param_name}_UsdUVTex")
    tex_node = UsdShade.Shader.Define(stage, tex_path)
    tex_node.CreateIdAttr("UsdUVTexture")
    tex_node.CreateInput("color_space", Sdf.ValueTypeNames.String).Set("raw" if "normal" in param_name else "sRGB")
    tex_node.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath(texture_path))
    tex_node.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
    tex_node.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
    tex_node.CreateOutput("a", Sdf.ValueTypeNames.Float)
    if "normal" in param_name:
        tex_node.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(2.0, 2.0, 2.0, 1.0))
        tex_node.CreateInput("bias", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(-1.0, -1.0, -1.0, 0.0))
        tex_node.CreateOutput("rgb", Sdf.ValueTypeNames.Normal3f)
    else:
        tex_node.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(1.0, 1.0, 1.0, 1.0))
        tex_node.CreateOutput("r", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("g", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("b", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f)

    # Define the UV Tile Node
    uv_node_path = tex_scope_path.AppendChild(f"{param_name}_UsdUVNode")
    uv_node = UsdShade.Shader.Define(stage, uv_node_path)
    uv_node.CreateIdAttr("UsdPrimvarReader_float2")
    uv_node.CreateInput("fallback", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(uv_tile.X, uv_tile.Y))
    uv_node.CreateInput("st", Sdf.ValueTypeNames.Token).Set("st")    
    uv_node.CreateOutput("result", Sdf.ValueTypeNames.Float2)

    tex_node.CreateInput("st", Sdf.ValueTypeNames.Token).ConnectToSource(uv_node.ConnectableAPI(), "result")


def compose_pfx_usd(asset_info_path: str, asset_alembic_path: str, 
                    payload_usd_path: str, asset_usd_path: str,
                    asset_name: str, asset_base_prim_path: str):
    """
    * Main function reading in the looks info to build the usd file.
    * @param asset_info_path        : type str : Path to the asset json we'll be reading in
    * @param asset_alembic_path     : type str : Path to the asset alembic path
    * @param payload_usd_path       : type str : Path to the payload USD path
    * @param asset_usd_path         : type str : Path to the asset USD path
    * @param asset_name             : type str  : Name of the asset
    * @param asset_base_prim_path   : type str  : The base prim path of the asset, generally "/render_GRP"
    """
    # Create the main payload file if it doesn't exist.
    usd_payload_stage: Usd.Stage = usd_stage(payload_usd_path)
    ups_root_prim: Usd.Prim = usd_root_prim(usd_payload_stage, asset_name, False)
    root_asset_info(ups_root_prim, asset_alembic_path, asset_name)
    asset_ref: Sdf.Reference = usd_reference(ups_root_prim, asset_alembic_path, asset_base_prim_path)
    usd_payload_stage.Save()

    # Create the actual asset definition usd
    usd_asset_stage: Usd.Stage = usd_stage(asset_usd_path)
    usd_asset_root_prim: UsdGeom.Xform = usd_root_prim(usd_asset_stage, asset_name)
    model_api = Usd.ModelAPI(usd_asset_root_prim)
    model_api.SetKind(Kind.Tokens.component)
    root_asset_info(usd_asset_root_prim, asset_alembic_path, asset_name)
    usd_asset_stage.Save()

    mat_list = ptusds.parse_looks_info(asset_info_path)
    for mat_info in mat_list:
        if mat_info.get('meshes'):
            for mesh in mat_info.get('meshes'):
                payload_path = '/'.join(mesh.split('|')[2:-1])
                mesh_payload_path = f'/{asset_name}/{payload_path}'
                usd_mesh_payload(usd_asset_stage, f'/{asset_name}/{mesh.split("|")[-1]}', payload_usd_path, mesh_payload_path)

    usd_create_mtlx(usd_asset_stage)
    usd_create_texture(usd_asset_stage, usd_asset_stage.GetPrimAtPath("/Looks"), "/blah/bleh/bluh", "base_color")
    usd_create_texture(usd_asset_stage, usd_asset_stage.GetPrimAtPath("/Looks"), "/blah/bleh/bluh_N", "normal")
    usd_create_texture(usd_asset_stage, usd_asset_stage.GetPrimAtPath("/Looks"), "/blah/bleh/bluh_CN", "coat_normal")

    usd_asset_stage.Save()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process the PFx Asset Info and generate a USDA file.')
    parser.add_argument('asset_info_path', metavar='-aip', type=str, help='The PFx Asset Info Path')
    parser.add_argument('asset_alembic_path', metavar='-abcp', type=str, help='The alembic mesh path')
    parser.add_argument('payload_usd_path', metavar='-pusdp', type=str, help='The path to the payload usd file')
    parser.add_argument('asset_usd_path', metavar='-ausdp', type=str, help='The path to the asset usd file')
    parser.add_argument('asset_name', metavar='-an', type=str, help='The asset name')
    parser.add_argument('asset_base_prim_path', metavar='-abpp', type=str, help='The default prim path of the asset')

    args = parser.parse_args()
    compose_pfx_usd(args.asset_info_path, args.asset_alembic_path, args.payload_usd_path, args.asset_usd_path, args.asset_name, args.asset_base_prim_path)

    #compose_pfx_usd("C:/Users/Mukund Dhananjay/Downloads/.LUK_Character_Alien.ma",
    #                "D:/USD/Alien/asset/GEO_Character_Alien.abc",
    #                "D:/USD/Alien/asset/usd/AlienPayload_New.usda",
    #                "D:/USD/Alien/asset/usd/GEO_Char_Alien_Body_New.usda",
    #                "Alien", "/render_GRP")