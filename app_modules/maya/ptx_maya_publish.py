from ...core import ptx_publish_factory as ppf
from .ptx_mdl_publish import PtxMdlPublishBuilder
from .ptx_luk_publish import PtxLukPublishBuilder

factory = ppf.PtxPublishFactory()
factory.register_app('MAYA', 'MDLP', PtxMdlPublishBuilder())
factory.register_app('MAYA', 'LUKP', PtxLukPublishBuilder())