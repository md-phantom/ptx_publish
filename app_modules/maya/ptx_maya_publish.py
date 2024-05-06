from ...core import ptx_publish_factory as ppf
from .ptx_mdl_publish import PtxMdlActiveBuilder, PtxMdlPassiveBuilder
from .ptx_luk_publish import PtxLukPublishBuilder

factory = ppf.PtxPublishFactory()
factory.register_app('MAYA', 'MDLA', PtxMdlActiveBuilder())
factory.register_app('MAYA', 'MDLP', PtxMdlPassiveBuilder())
factory.register_app('MAYA', 'LUKP', PtxLukPublishBuilder())