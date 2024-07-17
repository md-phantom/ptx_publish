from chitragupta.ptx_data_structs import ptx_usd_structs as pusds

from dataclasses import dataclass, field


@dataclass
class PhantomUsdMaterialPreview(pusds.PhantomUsdMaterialBase):
    """
    * Defines all properties in a USD Preview Surface Material
    """
    clearcoat: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    clearcoatRoughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    diffuseColor: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    emissiveColor: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    opacity: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    ior: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    metallic: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    normal: pusds.PhantomUsdVector3Attribute = field(default_factory=pusds.PhantomUsdVector3Attribute)
    roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    specularColor: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    displacement: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    occlusion: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)

    def __post_init__(self):
        """
        * Initialize the attribute names if they are empty
        """
        if self.clearcoat.name == '': self.clearcoat.name = 'clearcoat'
        if self.clearcoatRoughness.name == '': self.clearcoatRoughness.name = 'clearcoatRoughness'
        if self.diffuseColor.name == '': self.diffuseColor.name = 'diffuseColor'
        if self.emissiveColor.name == '': self.emissiveColor.name = 'emissiveColor'
        if self.opacity.name == '': self.opacity.name = 'opacity'
        if self.ior.name == '': self.ior.name = 'ior'
        if self.metallic.name == '': self.metallic.name = 'metallic'
        if self.normal.name == '': self.normal.name = 'normal'
        if self.roughness.name == '': self.roughness.name = 'roughness'
        if self.specularColor.name == '': self.specularColor.name = 'specularColor'
        if self.displacement.name == '': self.displacement.name = 'displacement'
        if self.occlusion.name == '': self.occlusion.name = 'occlusion'


class PhantomUsdMaterialBuilder:
    """
    * Factory to create a PhantomUsdMaterialPreview instance
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PhantomUsdMaterialPreview:
        if not self._instance:
            self._instance = PhantomUsdMaterialPreview(*args, **kwds)
        return self._instance


if __name__ == "__main__":
    matx = PhantomUsdMaterialPreview(name="Test", material_type=pusds.UsdMaterialType.StandardSurface, meshes=["mesh1", "mesh2"])
    print(matx)