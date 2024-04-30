"""
* A set of utilities for arnold in maya
"""
import pymel.core as pm
import os
import glob
import logging
import subprocess


def list_textures():
    """
    * Get a list of all textures in the scene
    """
    tex_list = list()
    all_tex = [tex.fileTextureName.get() for tex in pm.ls(type='file')]
    for tex in all_tex:
        f_name, ext = os.path.splitext(os.path.basename(tex))
        all_files = glob.glob(f"{os.path.dirname(tex)}/{f_name}.*.{ext}")
        for fl in all_files:
            if fl not in tex_list:
                tex_list.append(fl)
    return tex_list


def create_txfile(file_path, output_folder, task_id, show_name, rez_activate='P:/TOOLS/rez/activate_rez.cmd'):
    """
    * @param file_path: type str: path of the texture
    * @param output_folder: type str: path of where we want to store the tx files
    * @param task_id: type str: the task id of the process
    * @param show_name: type str: name of the show
    * @param rez_activate: type str: path to the rez.cmd
    * Starts a process to convert textures into arnold's native tx format
    """
    tx_file = file_path.replace(f"{os.path.splitext(file_path)[-1]}", '.tx')
    tx_out_file = f'{output_folder}/{os.path.basename(tx_file)}'.replace('\\', '/')
    env = f'set task_id={task_id}'
    cmd = f'{env}&& {rez_activate} && rez-env maya {show_name}_maya arnold --maketx '
    cmd += f'"-v" "-u" "-oiio" "--checknan" "ACEScg" {file_path.replace("\\", "/")} "--format" "exr" "-d" "half" '
    cmd += f'"--compression" "dwaa" "-o" "{tx_out_file}"'
    
    logging.info(f'cmd: {0}'.format(cmd))

    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = result.communicate()
    logging.info(out)
    logging.info(err)
    return (out, err)


def replace_txfiles():
    """
    * Replace the path to the texture file in the fileTextureNode to the equivalent .tx file path
    """
    tex_list = pm.ls(type='file')
    for tex in tex_list:
        tx_path = tex.fileTextureName.get()
        tex.fileTextureName.set(os.path.splitext(os.path.basename(tx_path))[0] + '.tx')
        tex.uvTilingMode.set(3)
