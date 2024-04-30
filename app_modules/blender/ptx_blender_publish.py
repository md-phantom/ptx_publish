from ...core import ptx_publish_factory as ppf
from .ptx_mdl_publish import PtxMdlPublishBuilder

factory = ppf.PtxPublishFactory()
factory.register_app('BLENDER', 'MDLP', PtxMdlPublishBuilder())
