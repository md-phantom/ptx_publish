"""
* A set of utilities for creating almebic files from Maya
"""
import pymel.core as pm
from pathlib import Path
import logging


def generate_abc_command(node_list, out_file, start, end, attr_list=[], no_normals=False, uv_write=True, write_color_sets=True, write_face_sets=True,
                         whole_frame_geo=True, world_space=True, write_visibility=True, strip_namespaces=True, euler_filter=True, auto_subd=True,
                         write_uv_sets=True, data_format="ogawa"):
    """
    * @param node: type str: Root node used for caching
    * @param out_file: type str: Path for the Alembic cache storage
    * @param start: type int: Start frame for Alembic cache
    * @param end: type int: End frame for Alembic cache
    * Generate the command template for running the alembic cache command in maya
    """    
    # Create the abc command with the frameRange
    abc_cmd = f"-frameRange {start} {end} -dataFormat {data_format}"

    # Add any extra attributes, if required
    for attr in attr_list:
        abc_cmd += f" -attr {attr}"

    # Add in the bool flags if needed
    abc_cmd = abc_cmd + " -noNormals" if no_normals else abc_cmd
    abc_cmd = abc_cmd + " -uvWrite" if uv_write else abc_cmd
    abc_cmd = abc_cmd + " -writeColorSets" if write_color_sets else abc_cmd
    abc_cmd = abc_cmd + " -writeFaceSets" if write_face_sets else abc_cmd
    abc_cmd = abc_cmd + " -wholeFrameGeo" if whole_frame_geo else abc_cmd
    abc_cmd = abc_cmd + " -worldSpace" if world_space else abc_cmd
    abc_cmd = abc_cmd + " -writeVisibility" if write_visibility else abc_cmd
    abc_cmd = abc_cmd + " -stripNamespaces" if strip_namespaces else abc_cmd
    abc_cmd = abc_cmd + " -eulerFilter" if euler_filter else abc_cmd
    abc_cmd = abc_cmd + " -autoSubd" if auto_subd else abc_cmd
    abc_cmd = abc_cmd + " -writeUVSets" if write_uv_sets else abc_cmd

    for node in node_list:
        nd = pm.PyNode(node)
        abc_cmd += f" -root {nd.longName()}"

    # Add in the file flag
    abc_cmd += f" -file \'{out_file}\'"

    logging.info(f"cmd: {abc_cmd}")
    return abc_cmd


def export_abc(abc_cmd_list, pre_roll=0):
    """
    * @param abc_cmd_list: type str list: the command(s) to pass to Maya's internal almebic caching plugin
    * @param pre_roll: type int: Num frames to do pre-roll from
    """
    pm.AbcExport(j=abc_cmd_list, verbose=False)


def import_gpu_cache(cache_path):
    """
    * @param cache_path: type str: the path of the file you want to import as the gpu_cache
    """
    # Create the gpu cache node and set the cacheFileName to the gpu cache path
    gpu_cache_name = Path(cache_path)
    gpu_cache_node = pm.createNode("gpuCache", n=(f"{gpu_cache_name.stem}GpuCacheShape"))
    gpu_cache_node.setAttr("cacheFileName", cache_path)
    pm.listRelatives(gpu_cache_node, parent=True, fullPath=True)[0].rename(gpu_cache_name.stem)
    return gpu_cache_node


def gpu_cache_to_geom(gpu_cache_node):
    """
    * @param gpu_cache_node: type pymel gpu cache node: The gpu cache node we want to make native to the file
    * In essence, will try and convert this gpu_cache into an editable version of the geometry.
    """
    transform = pm.listRelatives(gpu_cache_node, parent=True, fullPath=True)[0]
    file_path = gpu_cache_node.getAttr("cacheFileName")

    # delete the gpu cache node and it's transform
    pm.delete(transform)

    # import the geometry from the alembic cache
    pm.AbcImport(file_path, mode="import")