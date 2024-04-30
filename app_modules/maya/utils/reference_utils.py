"""
* A set of utilities to manage references inside a maya scene
"""
import pymel.core as pm
import logging


def clear_namespaces():
    """
    * Remove all namespaces in the scene, except for default references
    """
    logging.info('Cleaning Namespaces')
    namespaces = [ns for ns in pm.namespaceInfo(lon=1, r=1) if ns not in ['UI', 'shared']]

    # reverse iterate through the contents of the list to remove the deepest layers first
    for ns in reversed(namespaces):
        pm.namespace(rm=ns, mnr=1)

    namespaces[:] = []


def import_references():
    """
    * Import all references into the scene
    """
    logging.info('Importing References')
    refs = pm.listReferences()
    for ref in refs:
        ref.importContents()


def check_references(ref_path):
    """
    * @return: type bool
    * Check the given path against a list of all references in the scene and see if it's in the scene
    """
    logging.info('Checking if {ref_path} is already referred in the scene')
    curr_ref_paths = [rp.referencePath for rp in pm.ls(type='reference')]
    return True if (ref_path in curr_ref_paths) else False