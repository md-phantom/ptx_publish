from dataclasses import dataclass, fields
from pxr import Usd, Sdf, UsdGeom, Kind, Gf, UsdShade, Tf
from pathlib import Path
from typing import List
import os

from chitragupta.ptx_data_structs import ptx_usd_structs as ptusds
from ptx_publish.app_modules.usd.factories import phantom_usd_factory as puf

__MATERIALX_PARAM_WHITELIST__ = {"base": "base", "baseColor": "base_color", "diffuseRoughness": "diffuse_roughness", "normalColor": "normal", "tangent": "tangent",  
                                 "metalness": "metalness", "specular": "specular", "specularColor": "specular_color", "specularRoughness": "specular_roughness",
                                 "specularIOR": "specular_IOR", "specularAnisotropy": "specular_anisotropy", "specularRotation": "specular_rotation",
                                 "transmission": "transmission", "transmissionColor": "transmission_color", "transmissionDepth": "transmission_depth",
                                 "transmissionScatter": "transmission_scatter", "transmissionScatterAnisotropy": "transmission_scatter_anisotropy", 
                                 "transmissionDispersion": "transmission_dispersion", "transmissionExtraRoughness": "transmission_extra_roughness",
                                 "subsurface": "subsurface", "subsurfaceColor": "subsurface_color", "subsurfaceRadius": "subsurface_radius", "subsurfaceScale": "subsurface_scale",
                                 "subsurfaceAnisotropy": "subsurface_anisotropy", "sheen": "sheen", "sheenColor": "sheen_color", "sheenRoughness": "sheen_roughness",
                                 "coat": "coat", "coatColor": "coat_color", "coatRoughness": "coat_roughness", "coatIOR": "coat_IOR", "coatNormal": "coat_normal", 
                                 "coatAnisotropy": "coat_anisotropy", "coatRotation": "coat_rotation", "coatAffectColor": "coat_affect_color", 
                                 "coatAffectRoughness": "coat_affect_roughness", "thinFilmThickness": "thin_film_thickness", "thinFilmIOR": "thin_film_IOR", 
                                 "emission": "emission", "emissionColor": "emission_color", "opacity": "opacity", "thinWalled": "thin_walled"}


@dataclass
class PhantomMatStruct:
    material_type: str
    shader_name: str
    meshes: List
    parameters: List
    sg_node: str = ""


def convert_to_relative_path(abs_path: str, base_path: str) -> str:
    """
    Convert an absolute path to a relative path
    
    :param abs_path:    type str:    The absolute path to convert
    :param base_path:   type str:    The base path to convert from
    
    :return: type str
    """
    return os.path.relpath(abs_path, base_path)


def usd_stage(pfx_stage_path: str, stage_up_axis: UsdGeom.Tokens = UsdGeom.Tokens.y) -> Usd.Stage:
    """
    Take a path, and see if a USD stage exists here.
    If it exists, just open the stage and return it. If it doesn't, create a new usd stage
    at that location.
    :param pfx_stage_path:    type str:               The path of the USD stage on disk
    :param stage_up_axis:     type UsdGeom.Tokens:    The Up-Axis to use for this stage. By default, it's Y-Axis 
    
    :return: type Usd.Stage 
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
    See if the stage has a root prim, and if it exists, return it.
    If it doesn't, then create one, set it as the root and default prim, and return it.
    
    :param stage:             type Usd.Stage: The USD stage to add the root prim to
    :param root_prim_name:    type str:       The name of the Root Prim
    :param create_xform:      type bool:      Whether the Root Prim is an Xform or not. TODO: Support other types of prim
     
    :return: type Usd.Prim 
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
    Adds in the asset info on the given prim
     
    :param root_prim:     type Usd.Prim:  The USD prim to add the asset info to 
    :param asset_path:    type str:       The asset path we're adding in
    :param asset_name:    type str:       The asset name  
    """
    model_api = Usd.ModelAPI(root_prim)
    info = {
        'identifier': Sdf.AssetPath(asset_path), 
        'name': asset_name
    }
    
    model_api.SetAssetInfo(info)


def usd_reference(prim: Usd.Prim, asset_path: str, asset_prim_path: str) -> Sdf.Reference:
    """
    Search the prim for any reference with the asset_path and prim_path
    If it exists, return the reference, else, create it and return it.
     
    :param prim:              type Usd.Prim:  The USD prim to add the reference to
    :param asset_path:        type str:       The asset path to refer in
    :param asset_prim_path:   type str:       The path of the prim in the asset we want to refer in
    
    :return: type Sdf.Reference
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


def usd_mesh_payload(stage: Usd.Stage, prim_path: str, extern_payload_path: str, payload_prim_path: str) -> UsdGeom.Mesh:
    """
    Get the USD mesh prim with a payload, if it exists. If it doesn't exist, create one.
    
    :param stage:                     type Usd.Stage: The USD stage to add the scope to
    :param prim_path:                 type str:       The stage relative path of the primitive
    :param extern_payload_path:       type str:       The path to the payload on storage
    :param payload_prim_path:         type str:       The path of the payload in the alembic file
     
    :return: type UsdGeom.Mesh 
    """
    if stage.GetPrimAtPath(f'{prim_path}'):
        return stage.GetPrimAtPath(f'{prim_path}')
    
    mesh_payload: UsdGeom.Mesh = UsdGeom.Mesh.Define(stage, prim_path).GetPrim()
    mesh_payload.GetPayloads().AddPayload(
        assetPath = extern_payload_path,
        primPath = payload_prim_path
    )
    # add the material binding API
    UsdShade.MaterialBindingAPI.Apply(mesh_payload)
    return mesh_payload


def usd_scope(stage: Usd.Stage, parent_prim: Usd.Prim = None, scope_name: str = "Scope") -> Usd.Prim:
    """
    Define a scope in the stage. If we have a valid parent prim, define the scope
    under the prim, else define it at the root.
    
    :param stage:         type Usd.Stage: The USD stage to add the scope to
    :param parent_prim:   type Usd.Prim:  The Parent Prim to add this scope under
    :param scope_name:    type Usd.Prim:  The name of the scope
     
    :return: type Usd.Prim 
    """
    geom_scope: Usd.Prim = stage.DefinePrim(f"{parent_prim.GetPath().pathString}/{scope_name}" if parent_prim else f"/{scope_name}", "Scope")
    return geom_scope


def usd_create_mtlx(stage: Usd.Stage, parent_prim: Usd.Prim = None, mtl_name: str = "MtlX", mtl_param_list: list = [],
                    mtlx_type:str = "/__class_mtl__/mtlxmaterial", shader_type:str = "ND_standard_surface_surfaceshader") -> UsdShade.Material:
    """
    :Create a mtlx shader and override the parameters that need to be overridden.
    
    :param stage:          type Usd.Stage: The USD stage to add the mtlx to
    :param parent_prim:    type Usd.Prim:  The Parent Prim to add this mtlx under
    :param mtl_name:       type str:       The name of the material
    :param mtl_param_list: type list:      The list of parameters to override
    :param mtlx_type:      type str:       The type of mtlx shader. 
    :param shader_type:    type str:       The type of shader to create.
     
    :return: type UsdShade.Material 
    """
    # Get an instance of our USDMaterialX Node
    p_fac = puf.PhantomUsdFactory()
    mtl_spec = p_fac.register_usd_type("shaders", "aiStandardSurface")

    # Create a materialX node, but as of now we don't need to feed in the mesh list.
    mtlx_node = p_fac.create(mtl_spec, mtl_name, [])

    # Get the looks parent prim path
    looks_path = Sdf.Path(parent_prim.GetPath())

    # create the material definition from the template mtlx available to us
    mat_path = looks_path.AppendChild(f"{mtl_name}")
    mat_def = UsdShade.Material.Define(stage, mat_path)

    # hardcoding the material class for now; 
    # TODO: figure out where these definitions are, and how to add to these
    inherits = stage.GetPrimAtPath(mat_path).GetInherits()
    inherits.AddInherit(Sdf.Path(mtlx_type))

    # Create the MtlX surface shader definitions
    shd_std_srf = UsdShade.Shader.Define(stage, mat_path.AppendChild(f"{mtl_name}_standard_surface"))
    shd_std_srf.CreateIdAttr(shader_type)

    find_field = lambda usd_node, field_name: next((f for f in fields(usd_node) if f.name == field_name), None)
    
    for param in mtl_param_list:
        if param["name"] in __MATERIALX_PARAM_WHITELIST__.keys():
            fld = find_field(mtlx_node, __MATERIALX_PARAM_WHITELIST__[param["name"]])
            texture_info = param.get("texture")
            param_type = getattr(mtlx_node, fld.name).type
            if param_type == ptusds.UsdAttributeType.bool:
                shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Bool).Set(True if param["value"] == "true" else False)
            elif param_type == ptusds.UsdAttributeType.float:
                shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Float).Set(param["value"])
            elif param_type == ptusds.UsdAttributeType.vector3:
                val_arr = param["value"]
                if "texture" in param.keys():
                    tex_node, coord_node = usd_create_texture(stage, stage.GetPrimAtPath(mat_path), param["texture"]["path"], __MATERIALX_PARAM_WHITELIST__[param["name"]], ptusds.Float2(1.0, 1.0), mtl_name)
                    shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Normal3f).ConnectToSource(tex_node.ConnectableAPI(), "rgb")
                else:
                    shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Normal3f).Set(Gf.Vec3f(val_arr[0], val_arr[1], val_arr[2]))
            else:
                val_arr = param["value"]
                if "texture" in param.keys():
                    tex_node, coord_node = usd_create_texture(stage, stage.GetPrimAtPath(mat_path), param["texture"]["path"], __MATERIALX_PARAM_WHITELIST__[param["name"]], ptusds.Float2(1.0, 1.0), mtl_name)
                    shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Color3f).ConnectToSource(tex_node.ConnectableAPI(), "rgb")
                else:
                    shd_std_srf.CreateInput(fld.name, Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(val_arr[0], val_arr[1], val_arr[2]))

    # Create the MtlX displacement shader definitions
    shd_displ = UsdShade.Shader.Define(stage, mat_path.AppendChild("Displacement"))
    shd_displ.CreateIdAttr("ND_displacement_float")

    # Hook up the outputs of these shaders to the outputs on the main material
    mat_def.CreateSurfaceOutput("mtlx").ConnectToSource(shd_std_srf.ConnectableAPI(), "surface")
    mat_def.CreateDisplacementOutput("mtlx").ConnectToSource(shd_displ.ConnectableAPI(), "out")

    return mat_def


def usd_create_texture(stage: Usd.Stage, parent_prim: Usd.Prim, texture_path: str, param_name: str, uv_tile: ptusds.Float2 = ptusds.Float2(1.0, 1.0), mtl_name: str = "MtlX") -> tuple[UsdShade.Shader, UsdShade.Shader]:
    """
    Create a UsdUVTexture node, along with its associated uv coordinate node.
    We also handle creation for normal & tangent maps
    
    :param stage:         type Usd.Stage: The USD stage to create the texture under
    :param parent_prim:   type Usd.Prim:  The Parent Prim to add the texture under
    :param texture_path:  type str:       The path to the texture file
    :param param_name:    type str:       The name of the shader parameter we're adding to the material
    :param uv_tile:       type Float2:    The uv tiling value
    :param mtl_name:      type str:       The Material Name to which the texture belongs
    :param mtl_name:      type str:       The name of the material
    
    :return: type tuple(UsdShade.Shader, UsdShade.Shader)
    """
    # define the Textures scope
    tex_scope_path = Sdf.Path(parent_prim.GetPath().AppendChild(f"{mtl_name}Textures"))
    tex_scope = stage.DefinePrim(tex_scope_path, "Scope")

    # Define the UsdUV Texture
    tex_path = tex_scope_path.AppendChild(f"{param_name}_UsdUVTex")
    tex_node = UsdShade.Shader.Define(stage, tex_path)

    # Create inputs for file, wrapS, wrapT and an output for alpha
    tex_node.CreateIdAttr("ND_UsdUVTexture")
    tex_node.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath(texture_path))
    tex_node.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
    tex_node.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
    tex_node.CreateOutput("a", Sdf.ValueTypeNames.Float)

    # Create specific inputs for normal or tangent maps
    if "normal" in param_name or "tangent" in param_name:
        tex_node.CreateInput("color_space", Sdf.ValueTypeNames.String).Set("raw")
        tex_node.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(2.0, 2.0, 2.0, 1.0))
        tex_node.CreateInput("bias", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(-1.0, -1.0, -1.0, 0.0))
        tex_node.CreateOutput("rgb", Sdf.ValueTypeNames.Normal3f)
    else:
        tex_node.CreateInput("color_space", Sdf.ValueTypeNames.String).Set("sRGB")
        tex_node.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(1.0, 1.0, 1.0, 1.0))
        tex_node.CreateOutput("r", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("g", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("b", Sdf.ValueTypeNames.Float)
        tex_node.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f)

    # Define the UV Tile Node
    uv_node_path = tex_scope_path.AppendChild(f"{param_name}_UsdUVNode")
    uv_node = UsdShade.Shader.Define(stage, uv_node_path)
    uv_node.CreateIdAttr("ND_texcoord_vector2")
    uv_node.CreateInput("index", Sdf.ValueTypeNames.Int).Set(0)    
    uv_node.CreateOutput("out", Sdf.ValueTypeNames.Float2)

    tex_node.CreateInput("st", Sdf.ValueTypeNames.Token).ConnectToSource(uv_node.ConnectableAPI(), "out")

    return (tex_node, uv_node)


def usd_apply_material(prim: Usd.Prim, mtl_name: str, mtl: UsdShade.Material, mesh_list: List[UsdGeom.Mesh]):
    """
    Bind the given material to the list of meshes provided. We will use the collection method to bind the
    materials to the meshes
    
    :param prim:      type Usd.Prim:              The USD Prim which is the parent of the list of meshes
    :param mtl_name:  type str:                   Name of the Material we want to create the binding for
    :param mtl        type UsdShade.Material:     The Material Primitive to to create the binding for
    :param mesh_list: type List[UsdGeom.Mesh]:    The list of USD Meshes to bind the material to
    """
    mat_bind_api = UsdShade.MaterialBindingAPI.Apply(prim)
    collection_name = f"mat_bind_{mtl_name}"
    collection_api = Usd.CollectionAPI.Apply(prim, collection_name)
    for each_mesh in mesh_list:
        collection_api.GetIncludesRel().AddTarget(each_mesh.GetPath())
    
    collection_api.GetExpansionRuleAttr().Set(Usd.Tokens.expandPrims)
    mat_bind_api.Bind(collection_api, mtl, collection_name) 


def compose_pfx_usd(asset_info_path: str, asset_alembic_path: str, 
                    usd_base_location: str, asset_type: str,
                    asset_name: str, asset_base_prim_path: str):
    """
    Main function for reading in the looks info to build the USD payload, asset and look files.
    This can be used as is, or can be used as a reference on how to use the methods in this module
    to build out a USD file from scratch.
    
    :param asset_info_path        : type str : Path to the asset json we'll be reading in
    :param asset_alembic_path     : type str : Path to the asset alembic path
    :param usd_base_location      : type str : Path to where the payload and asset USD files will be saved
    :param asset_type             : type str : The type of the asset
    :param asset_name             : type str : Name of the asset
    :param asset_base_prim_path   : type str : The base prim path of the asset, generally "/render_GRP"
    """
    # Create the main payload file if it doesn't exist.
    payload_usd_path = f"{usd_base_location}/Payload_{asset_type}_{asset_name}.usda"
    usd_payload_stage: Usd.Stage = usd_stage(payload_usd_path)
    ups_root_prim: Usd.Prim = usd_root_prim(usd_payload_stage, asset_name, False)
    root_asset_info(ups_root_prim, asset_alembic_path, asset_name)
    asset_ref: Sdf.Reference = usd_reference(ups_root_prim, asset_alembic_path, asset_base_prim_path)
    usd_payload_stage.Save()

    # Create the actual asset definition usd
    asset_usd_path = f"{usd_base_location}/GEO_{asset_type}_{asset_name}.usda"
    usd_asset_stage: Usd.Stage = usd_stage(asset_usd_path)
    usd_asset_root_prim: UsdGeom.Xform = usd_root_prim(usd_asset_stage, asset_name)
    model_api = Usd.ModelAPI(usd_asset_root_prim)
    model_api.SetKind(Kind.Tokens.component)
    root_asset_info(usd_asset_root_prim, asset_alembic_path, asset_name)
    usd_asset_stage.Save()

    # Create the Looks USD stage.
    luk_usd_path = f"{usd_base_location}/LUK_{asset_type}_{asset_name}/LUK_{asset_type}_{asset_name}.usda"
    usd_look_stage: Usd.Stage = usd_stage(luk_usd_path)

    # Add the Looks scope
    usd_look_root_prim: Usd.Prim = usd_scope(usd_look_stage, None, "Looks")

    mat_list = ptusds.parse_looks_info(asset_info_path)
    mat_dict = {}
    for mat_info in mat_list:
        mat_struct = PhantomMatStruct(**mat_info)
        mat: UsdShade.Material = usd_create_mtlx(usd_look_stage, usd_look_root_prim, mat_struct.shader_name, mat_struct.parameters)
        mat_dict[mat] = {"name": mat_struct.shader_name, "mesh_list":[]}    
        for mesh in mat_struct.meshes:
            payload_path = '/'.join(mesh.split('|')[2:-1])
            mesh_payload_path = f'/{asset_name}/{payload_path}'
            mesh_payload = usd_mesh_payload(usd_asset_stage, f'/{asset_name}/{mesh.split("|")[-1]}', f"./Payload_{asset_type}_{asset_name}.usda", mesh_payload_path)
            mat_dict[mat]["mesh_list"].append(mesh_payload)
    
    # Save the Looks Stage File
    usd_look_stage.Save()

    # Reference the newly created looks usda into the asset usda
    usd_asset_looks_scope = usd_scope(usd_asset_stage, None, "Looks")
    looks_ref: Sdf.Reference = usd_reference(usd_asset_looks_scope, f"./LUK_{asset_type}_{asset_name}/LUK_{asset_type}_{asset_name}.usda", "/Looks")

    # Apply the materials in the Look file
    for each_mat in mat_dict:
        usd_apply_material(usd_asset_root_prim, mat_dict[each_mat]["name"], each_mat, mat_dict[each_mat]["mesh_list"])

    usd_asset_stage.Save()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process the PFx Asset Info and generate a USDA file.')
    parser.add_argument('asset_info_path', metavar='-aip', type=str, help='The PFx Asset Info Path')
    parser.add_argument('asset_alembic_path', metavar='-abcp', type=str, help='The alembic mesh path')
    parser.add_argument('usd_base_location', metavar='-usdbl', type=str, help='The path to the payload usd file')
    parser.add_argument('asset_type', metavar='-at', type=str, help='The path to the asset usd file')
    parser.add_argument('asset_name', metavar='-an', type=str, help='The asset name')
    parser.add_argument('asset_base_prim_path', metavar='-abpp', type=str, help='The default prim path of the asset')

    args = parser.parse_args()
    compose_pfx_usd(args.asset_info_path, args.asset_alembic_path, args.usd_base_location, args.asset_type, args.asset_name, args.asset_base_prim_path)

    #mat_list = ptusds.parse_looks_info("C:/Users/Mukund Dhananjay/Downloads/.LUK_Character_Alien.ma")
    #for mat in mat_list:
    #    mtl_struct = PhantomMatStruct(**mat)
    #    print(mtl_struct)
    #compose_pfx_usd("C:/Users/Mukund Dhananjay/Downloads/.LUK_Character_Alien.ma",
    #                "D:/USD/Alien/asset/GEO_Character_Alien.abc",
    #                "D:/USD/Alien/asset",
    #                "Character",
    #                "Alien", "/render_GRP")