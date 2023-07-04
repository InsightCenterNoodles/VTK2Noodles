"""Test script for testing geometry creation library

Offers sample methods a server could implement using a sphere
"""
import numpy as np
import logging
import pandas as pd
import matplotlib
from VtkNoodlesSourceStrainer import SourceStrainer
from VTKreaderStrainer import VTPnoodStrainer
from vtkmodules.vtkFiltersSources import vtkCylinderSource, vtkSphereSource, vtkArrowSource, vtkSuperquadricSource, vtkDiskSource
import rigatoni
from rigatoni.core import Server
from rigatoni import geometry as geo
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkFiltersHyperTree import vtkHyperTreeGridToUnstructuredGrid
from vtkmodules.vtkFiltersSources import vtkHyperTreeGridSource
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def create_sphere(server: rigatoni.Server, context, *args):
    """Test method to create 1 sphere"""

    name = "Test Sphere"
    material = server.create_component(rigatoni.Material, name="Test Material")

    source = vtkHyperTreeGridSource()
    source.SetDimensions(4, 4, 3)  # GridCell 3, 3, 2
    source.SetGridScale(1.5, 1.0, 0.7)
    source.SetBranchFactor(4)
    source.Update()
    
    data = []
    data = SourceStrainer(source.GetOutputPort())

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(-3, -3, 0, 0)],
        colors=[(127,0, 255)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")


    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1
def create_arrow(server: rigatoni.Server, context, *args):
    """Create vtk arrow"""

    name = "Arrow"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    arrow = vtkArrowSource()
    arrow.SetTipLength(3.0)
    arrow.SetShaftRadius(0.8)
    arrow.Update()

    data = []

    data = SourceStrainer(arrow)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(3, 3, 3, 1)],
        colors=[(265,0, 5)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1

def main_building(server: rigatoni.Server, context, *args):
    """creates castle building"""

    name = "main building"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    sphere = vtkCylinderSource()
    sphere.SetRadius(1)
    sphere.SetHeight(4)
    sphere.SetCenter(0,0,0)
    sphere.Update()

    data = []

    data = SourceStrainer(sphere)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        normals = data[2],
        textures = data[3],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0,0, 0)],
        colors=[(0,102, 102)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1

def side_towers(server: rigatoni.Server, context, *args):
    """method to create side towers"""

    name = "Side Towers"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    tower = vtkCylinderSource()
    tower.SetRadius(0.4)
    tower.SetHeight(6)
    tower.Update()

    data = []

    data = SourceStrainer(tower)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(1.6, 0, 0), (-1.6,0,0)],
        colors=[(260,80, 0)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1
def central_tower(server: rigatoni.Server, context, *args):
    """Method for Central Tower"""

    name = "Test Sphere"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    tower = vtkCylinderSource()
    tower.SetRadius(1)
    tower.SetHeight(6)
    tower.Update()

    data = []

    data = SourceStrainer(tower)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        normals = data[2],
        textures = data[3],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0, 0, 6)],
        colors=[(183,130, 189)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1
def rear_towers(server: rigatoni.Server, context, *args):
    """Test method to create two spheres"""

    name = "Test Sphere"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    tower = vtkCylinderSource()
    tower.SetRadius(0.4)
    tower.SetHeight(4)
    tower.Update()

    data = []

    data = SourceStrainer(tower)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        normals = data[2],
        textures = data[3],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(3.2, 0, 6), (-3.2,0,6)],
        colors=[(260,80, 0)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1
def spire(server: rigatoni.Server, context, *args):
    """Test method to create two spheres"""

    name = "Test Sphere"
    # uri_server = geo.ByteServer(port=40000)
    material = server.create_component(rigatoni.Material, name="Test Material")

    tower = vtkCylinderSource()
    tower.SetRadius(0.6)
    tower.SetHeight(4)
    tower.Update()

    data = []

    data = SourceStrainer(tower)

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices= data[0],
        indices= data[1],
        normals = data[2],
        textures = data[3],
        index_type="TRIANGLES",
        material=material.id,
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))

    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0,0,12)],
        colors=[(260,80, 150)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    #geo.export_mesh(server, sphere, "tests/mesh_data/test_sphere.obj")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    # light2 = server.create_component(rigatoni.Light, name="Sun", intensity=5, directional=rigatoni.DirectionalLight())
    #server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 3, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    direction_info = rigatoni.DirectionalLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 5, 0, 1
    ]
    directional = server.create_component(rigatoni.Light, name="Test Spot Light", directional=direction_info)
    #server.create_component(rigatoni.Entity, transform=mat, lights=[directional.id])

    return 1
def create_new_instance(server: rigatoni.Server, context, entity_id: list[int], position=None, color=None,
                        rotation=None, scale=None):
    """Method to test instance updating"""

    entity = server.get_delegate(rigatoni.EntityID(*entity_id))
    new_instance = geo.create_instances(position, color, rotation, scale)
    geo.add_instances(server, entity, new_instance)


def normalize_df(df: pd.DataFrame):
    """Helper to normalize values in a dataframe"""

    normalized_df = df.copy()
    for column in normalized_df:
        normalized_df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())

    return normalized_df


def make_point_plot(server: rigatoni.Server, context, *args):
    """Test Method to generate plot-like render from data.csv"""

    name = "Test Plot"
    material = server.create_component(rigatoni.Material, name="Test Material")

    # Add Lighting
    point_info = rigatoni.PointLight(range=-1)
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        3, 3, 3, 1
    ]
    light = server.create_component(rigatoni.Light, name="Test Point Light", point=point_info)
    sun = server.create_component(rigatoni.Light, name="Sun", intensity=1, directional=rigatoni.DirectionalLight())
    server.create_component(rigatoni.Entity, transform=mat, lights=[light.id])

    spot_info = rigatoni.SpotLight()
    mat = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 3, 0, 1
    ]
    spot = server.create_component(rigatoni.Light, name="Test Spot Light", spot=spot_info)
    server.create_component(rigatoni.Entity, transform=mat, lights=[spot.id])

    # Create patch / geometry for point geometry
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices=vertices,
        indices=indices,
        index_type="TRIANGLES",
        material=material.id
    )
    patches.append(geo.build_geometry_patch(server, name, patch_info))
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Read data from data.csv and normalize
    df = pd.read_csv("tests/mesh_data/data.csv")
    df_scaled = normalize_df(df)

    # Positions
    x = list(df_scaled['Total_CNG'].apply(lambda x: x * 5 - 2.5))
    y = list(df_scaled['Total_Elec'].apply(lambda x: x * 5))
    z = list(df_scaled['Elec_price_incentive'].apply(lambda x: x * 5 - 2.5))

    # Colors
    cmap = matplotlib.cm.get_cmap("plasma")
    cols = df_scaled['CNG_price_incentive']
    cols = [cmap(i) for i in cols]

    # Scales
    s = .1
    scls = [(i * s, i * s, i * s, i * s) for i in list(df_scaled['FCI_incentive_amount[CNG]'])]

    # Create instances of sphere to represent csv data in an entity
    instances = geo.create_instances(
        positions=[*zip(x, y, z)],
        colors=cols,
        scales=scls
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    # new_instance = geo.create_instances([[1,1,1]])
    # geo.add_instances(server, entity, new_instance)
    return 0


def create_from_mesh(server: rigatoni.Server, context, *args):
    """Test Method to generate render from mesh"""

    name = "Test Mesh"
    material = server.create_component(rigatoni.Material, name="Test Material")

    # use libraries from mesh option    
    uri_server = geo.ByteServer(port=60000)
    server.byte_server = uri_server
    mesh = geo.geometry_from_mesh(server, "tests/mesh_data/stanford-bunny.obj", material,
                                  name, uri_server, generate_normals=False)
    # mesh = geo.geometry_from_mesh(server, "mesh_data/test_sphere.vtk", material)
    # mesh = geo.geometry_from_mesh(server, "mesh_data/magvort.x3d", material, name, uri_server, generate_normals=False)
    # mesh = geo.geometry_from_mesh(server, "mesh_databoot.obj", material, name, uri_server)

    # Create instances of sphere to represent csv data in an entity
    instances = geo.create_instances()
    entity = geo.build_entity(server, geometry=mesh, instances=instances)

    # Test export
    geo.export_mesh(server, mesh, "tests/mesh_data/test_mesh.obj", uri_server)
    return 0


def delete_sphere(server: rigatoni.Server, context, *args):
    sphere = server.get_delegate_id("Test Sphere")
    server.delete_component(sphere)

    return 0


def move_sphere(server: rigatoni.Server, context, *args):
    # Change world transform, but do you change local?
    sphere = server.get_delegate("Test Sphere")
    # sphere.transform = [
    #     1, 0, 0, 0,
    #     0, 1, 0, 0,
    #     0, 0, 1, 0,
    #     args[0], args[1], args[2], 1
    # ]
    sphere.transform = [
        1, 0, 0, args[0],
        0, 1, 0, args[1],
        0, 0, 1, args[2],
        0, 0, 0, 1
    ]
    server.update_component(sphere)
    pass


# define arg documentation for injected method
instance_args = [
    rigatoni.MethodArg(name="entity id", doc="What're you creating an instance of?", editor_hint="noo::entity_id"),
    rigatoni.MethodArg(name="position", doc="Where are you putting this instance? vec3", editor_hint="noo::array"),
    rigatoni.MethodArg(name="color", doc="What color is this instance? RGBA Vector", editor_hint="noo::array"),
    rigatoni.MethodArg(name="rotation", doc="How is this instance rotated? Vec4", editor_hint="noo::array"),
    rigatoni.MethodArg(name="scale", doc="How is this instance scaled? Vec3", editor_hint="noo::array")
]

move_args = [
    rigatoni.MethodArg(name="x", doc="How far to move in x", editor_hint="noo::real"),
    rigatoni.MethodArg(name="y", doc="How far to move in y", editor_hint="noo::real"),
    rigatoni.MethodArg(name="z", doc="How far to move in z", editor_hint="noo::real")
]

# Define starting state
starting_state = [
    rigatoni.StartingComponent(rigatoni.Method, {"name": "new_point_plot", "arg_doc": []}, make_point_plot),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_new_instance", "arg_doc": [*instance_args]},create_new_instance),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_sphere", "arg_doc": []}, create_sphere),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_arrow", "arg_doc": []}, create_arrow),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_main_building", "arg_doc": []}, main_building),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_side_towers", "arg_doc": []}, side_towers),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_central_tower", "arg_doc": []}, central_tower),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_rear_towers", "arg_doc": []}, rear_towers),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_spire", "arg_doc": []}, spire),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "delete_sphere", "arg_doc": []}, delete_sphere),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "move_sphere", "arg_doc": [*move_args]}, move_sphere),
]

logging.basicConfig(
    format="%(message)s",
    level=logging.DEBUG
)


def main():

    server = Server(50000, starting_state)
    server.run()


if __name__ == "__main__":
    main()
