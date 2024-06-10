from ...core import ptx_publish_factory as ppf
from .ptx_mdl_active import PtxNodeBuilder as mdla_ptx_nodebuilder
from .ptx_mesh_cache import PtxNodeBuilder as mdlp_ptx_nodebuilder
from .ptx_luk_publish import PtxLukPublishBuilder

factory = ppf.PtxPublishFactory()
factory.register_app('MAYA', 'MDLA', mdla_ptx_nodebuilder())
factory.register_app('MAYA', 'MDLP', mdlp_ptx_nodebuilder())
factory.register_app('MAYA', 'LUKP', PtxLukPublishBuilder())