from chitragupta.ptx_data_structs import ptx_usd_structs as pusds

from dataclasses import dataclass, field


@dataclass
class PhantomUsdMaterialX(pusds.PhantomUsdMaterialBase):
    """
    * Defines all properties in a MaterialX node
    """     
    base: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    base_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    diffuse_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    normal: pusds.PhantomUsdVector3Attribute = field(default_factory=pusds.PhantomUsdVector3Attribute)
    tangent: pusds.PhantomUsdVector3Attribute = field(default_factory=pusds.PhantomUsdVector3Attribute)

    metalness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    
    specular: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    specular_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    specular_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    specular_IOR: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    specular_anisotropy: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    specular_rotation: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)

    transmission: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    transmission_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    transmission_depth: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    transmission_scatter: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    transmission_scatter_anisotropy: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    transmission_dispersion: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    transmission_extra_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)

    subsurface: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    subsurface_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    subsurface_radius: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    subsurface_scale: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    subsurface_anisotropy: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)

    sheen: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    sheen_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    sheen_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    
    coat: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    coat_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_anisotropy: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_rotation: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_IOR: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_normal: pusds.PhantomUsdVector3Attribute = field(default_factory=pusds.PhantomUsdVector3Attribute)
    coat_affect_color: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    coat_affect_roughness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)

    thin_film_thickness: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    thin_film_IOR:pusds. PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    
    emission: pusds.PhantomUsdFloatAttribute = field(default_factory=pusds.PhantomUsdFloatAttribute)
    emission_color: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)

    opacity: pusds.PhantomUsdColor3Attribute = field(default_factory=pusds.PhantomUsdColor3Attribute)
    
    thin_walled: pusds.PhantomUsdBoolAttribute = field(default_factory=pusds.PhantomUsdBoolAttribute)

    def __post_init__(self):
        """
        * Initialize the attribute names if they are empty
        """
        # Set the material type
        self.material_type = pusds.UsdMaterialType.StandardSurface

        # set any default values which may not have been passed in
        if self.base.name == '': self.base.name = 'base'
        if self.base_color.name == '': self.base_color.name = 'base_color'
        if self.diffuse_roughness.name == '': self.diffuse_roughness.name = 'diffuse_roughness'
        if self.normal.name == '': self.normal.name = 'normal'
        if self.tangent.name == '': self.tangent.name = 'tangent'
        if self.metalness.name == '': self.metalness.name = 'metalness'
        if self.specular.name == '': self.specular.name = 'specular'
        if self.specular_color.name == '': self.specular_color.name = 'specular_color'
        if self.specular_roughness.name == '': self.specular_roughness.name = 'specular_roughness'
        if self.specular_IOR.name == '': self.specular_IOR.name = 'specular_IOR'
        if self.specular_anisotropy.name == '': self.specular_anisotropy.name = 'specular_anisotropy'
        if self.specular_rotation.name == '': self.specular_rotation.name = 'specular_rotation'
        if self.transmission.name == '': self.transmission.name = 'transmission'
        if self.transmission_color.name == '': self.transmission_color.name = 'transmission_color'
        if self.transmission_depth.name == '': self.transmission_depth.name = 'transmission_depth'
        if self.transmission_scatter.name == '': self.transmission_scatter.name = 'transmission_scatter'
        if self.transmission_scatter_anisotropy.name == '': self.transmission_scatter_anisotropy.name = 'transmission_scatter_anisotropy'
        if self.transmission_dispersion.name == '': self.transmission_dispersion.name = 'transmission_dispersion'
        if self.transmission_extra_roughness.name == '': self.transmission_extra_roughness.name = 'transmission_extra_roughness'
        if self.subsurface.name == '': self.subsurface.name = 'subsurface'
        if self.subsurface_color.name == '': self.subsurface_color.name = 'subsurface_color'
        if self.subsurface_radius.name == '': self.subsurface_radius.name = 'subsurface_radius'
        if self.subsurface_scale.name == '': self.subsurface_scale.name = 'subsurface_scale'
        if self.subsurface_anisotropy.name == '': self.subsurface_anisotropy.name = 'subsurface_anisotropy'
        if self.sheen.name == '': self.sheen.name = 'sheen'
        if self.sheen_color.name == '': self.sheen_color.name = 'sheen_color'
        if self.sheen_roughness.name == '': self.sheen_roughness.name = 'sheen_roughness'
        if self.coat.name == '': self.coat.name = 'coat'
        if self.coat_color.name == '': self.coat_color.name = 'coat_color'
        if self.coat_roughness.name == '': self.coat_roughness.name = 'coat_roughness'
        if self.coat_anisotropy.name == '': self.coat_anisotropy.name = 'coat_anisotropy'
        if self.coat_rotation.name == '': self.coat_rotation.name = 'coat_rotation'
        if self.coat_IOR.name == '': self.coat_IOR.name = 'coat_IOR'
        if self.coat_normal.name == '': self.coat_normal.name = 'coat_normal'
        if self.coat_affect_color.name == '': self.coat_affect_color.name = 'coat_affect_color'
        if self.coat_affect_roughness.name == '': self.coat_affect_roughness.name = 'coat_affect_roughness'
        if self.thin_film_thickness.name == '': self.thin_film_thickness.name = 'thin_film_thickness'
        if self.thin_film_IOR.name == '': self.thin_film_IOR.name = 'thin_film_IOR'
        if self.emission.name == '': self.emission.name = 'emission'
        if self.emission_color.name == '': self.emission_color.name = 'emission_color'
        if self.opacity.name == '': self.opacity.name = 'opacity'
        if self.thin_walled.name == '': self.thin_walled.name = 'thin_walled'


class PhantomUsdNodeBuilder:
    """
    * Factory for Creating an instance of the PhantomUsdMaterialX Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PhantomUsdMaterialX:
        if not self._instance:
            self._instance = PhantomUsdMaterialX(*args, **kwds)
        return self._instance


if __name__ == "__main__":
    from dataclasses import fields
    matx = PhantomUsdMaterialX(name="Test", meshes=["mesh1", "mesh2"])
    subsurface_field = lambda obj, field_name: next((f for f in fields(obj) if f.name == field_name), None)
    result = subsurface_field(matx, "subsurface")
    print(result.name, getattr(matx, result.name).type)