"""
* A set of utilities for creating almebic files from Maya
"""
import pymel.core as pm
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
                '-root {node} -writeVisibility -stripNamespaces -eulerFilter -autoSubd -writeUVSets ' \
                '-dataFormat ogawa -file \'{out_file}\''

    logging.info("cmd: {0}".format(abc_cmd))
    return abc_cmd


def do_pre_roll(pre_roll_frames):
    """
    * @param pre_roll_frames: type int: Num frames to do pre-roll from
    """
    logging.info("Doing PreRoll")


def export_abc(abc_cmd_list, pre_roll=0):
    """
    * @param abc_cmd_list: type str list: the command(s) to pass to Maya's internal almebic caching plugin
    * @param pre_roll: type int: Num frames to do pre-roll from
    """
    if pre_roll > 0:
        do_pre_roll(pre_roll)
    pm.AbcExport(j=abc_cmd_list, verbose=False)