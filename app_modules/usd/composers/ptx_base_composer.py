from pxr import Usd, Sdf, UsdGeom, Kind
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