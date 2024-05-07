"""
* A set of utilities for creating almebic files from Maya
"""
import pymel.core as pm
from pathlib import Path
import logging


def generate_abc_command(node, out_file, start, end):
    """
    * @param node: type str: Root node used for caching
    * @param out_file: type str: Path for the Alembic cache storage
    * @param start: type int: Start frame for Alembic cache
    * @param end: type int: End frame for Alembic cache
    * Generate the command template for running the alembic cache command in maya
    """
    abc_cmd = f'-frameRange {start} {end} -attr project -attr scope -attr taskType -attr artist -noNormals ' \
                '-uvWrite -writeColorSets -writeFaceSets -wholeFrameGeo -worldSpace ' \
                f'-root {node} -writeVisibility -stripNamespaces -eulerFilter -autoSubd -writeUVSets ' \
                f'-dataFormat ogawa -file \'{out_file}\''

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