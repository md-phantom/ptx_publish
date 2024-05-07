"""
* A set of utilities for creating usd files from Maya
"""
import pymel.core as pm
from pathlib import Path
import logging


def export_usd(file:str, append=False, chaser="", chaserArgs=[], convertMaterialsTo="UsdPreviewSurface", compatibility="", defaultCameras=False, 
               defaultMeshScheme="catmullClark", defaultUSDFormat="usda", eulerFilter=False, exportBlendShapes=False, exportCollectionBasedBindings=False,
               exportColorSets=True, exportDisplayColor=False, exportInstances=True, exportMaterialCollections=True, exportReferenceObjects=False, 
               exportRefsAsInstanceable=False, exportRoots="", exportSkels="", exportSkin="", exportUVs=True, exportVisibility=True, filterTypes="",
               frameRange=[1, 1], frameSample=0.0, frameStride=1.0, geomSidedness="derived", ignoreWarnings=False, kind="", materialCollectionsPath="",
               materialsScopeName="Looks", melPerFrameCallback="", melPostCallback="",  mergeTransformAndShape=True, normalizeNurbs=False, parentScope="",
               pythonPerFrameCallback="", pythonPostCallback="", renderLayerMode="defaultLayer", renderableOnly=True,
               selection=False, shadingMode="useRegistry", staticSingleSample=False, stripNamespaces=False, verbose=False):
    """
    * Export a USD file to disk
    """
    # Load the mayaUsdPlugin if it's not loaded
    if not pm.pluginInfo("mayaUsdPlugin", q=True, l=True):
        pm.loadPlugin("mayaUsdPlugin")

    # If selection is true and nothing is selected, select all top level assemblies
    # which are not the default cameras
    if selection and len(pm.ls(sl=True)) == 0:
        pm.select([node for node in pm.ls(assemblies=True) if node not in ['persp', 'top', 'front', 'side']])
        logging.info("Selected objects: {0}".format("|".join(pm.ls(sl=True))))

    # export the USD file
    pm.mayaUSDExport(**locals())


def import_usd(file:str, apiSchema="", chaser="", chaserArgs=[], excludePrimVar="", frameRange=[1, 1], importInstances="", importUSDZTextures=False,
               importUSDZTexturesFilePath="", metadata="", parent="", primPath="", preferredMaterial="", readAnimData=False, shadingMode=[],
               useAnimationCache=False, variant=[], verbose=False):
    """
    * Import a USD file from disk into the scene
    """
    # Load the mayaUsdPlugin if it's not loaded
    if not pm.pluginInfo("mayaUsdPlugin", q=True, l=True):
        pm.loadPlugin("mayaUsdPlugin")

    # Import the USD file into the scene
    pm.mayaUSDImport(**locals())


def nativize_stage(usd_stage, **kwargs):
    """
    * Take the usd_stage passed here and import the usd file associated with it into the scene
    """
    if not usd_stage:
        logging.error("No stage passed to nativize")

    # Sanity check to cast usd_stage as a PyNode of type mayaUsdProxyShape
    usd_stage = pm.PyNode(usd_stage)
    if usd_stage.nodeType() == pm.nt.Transform:
        usd_stage = usd_stage.listRelatives(children=True, typ="mayaUsdProxyShape")[0]

    # Import the usd file linked to this node as native geometry
    import_usd(file=usd_stage.getAttr("filePath"), **kwargs)

    # delete the USD stage
    pm.delete(usd_stage.listRelatives(parent=True, fullPath=True)[0])


def create_usd_stage(usd_path):
    """
    * Refer a usd file into the maya scene as a usd stage
    """
    # Create the usd stage node and set the filePath to the usd path
    usd_name = Path(usd_path)
    usd_stage_node = pm.createNode("mayaUsdProxyShape", n=(f"{usd_name.stem}UsdShape"))
    usd_stage_node.setAttr("filePath", usd_path)
    pm.listRelatives(usd_stage_node, parent=True, fullPath=True)[0].rename(usd_name.stem)