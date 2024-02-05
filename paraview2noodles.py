
import sys
sys.path.append('pathto/Rigatoni-main')
from typing import List, Optional
import numpy as np
import quaternion
from VtkNoodlesSourceStrainer import SourceStrainer
from Threading_withT import threading_strainer
from Reader_Strainer import noodStrainer
import rigatoni
from rigatoni.core import Server
from rigatoni import geometry as geo
import os
import logging
from rigatoni import ByteServer


class EntityDelegate(rigatoni.Entity):
    """Custom Entity that stores scale, rotation, and position as attributes"""
    scale: Optional[List[float]] = [1.0, 1.0, 1.0]
    rotation: Optional[List[float]] = [1.0, 0.0, 0.0, 0.0]
    position: Optional[List[float]] = [0.0, 0.0, 0.0]

    def update_transform(self):
        transform = np.eye(4)
        transform[3, :3] = self.position
        transform[:3, :3] = quaternion.as_rotation_matrix(np.quaternion(*self.rotation)).T
        transform[:3, :3] = np.matmul(np.diag(self.scale), transform[:3, :3])
        self.transform = transform.flatten().tolist()


def move(server: rigatoni.Server, context, vec):
    entity = server.get_delegate(context)
    entity.position = vec
    entity.update_transform()
    server.update_component(entity)


def rotate(server: rigatoni.Server, context, quat):
    entity = server.get_delegate(context)
    rearranged = [quat[3], quat[0], quat[1], quat[2]]
    entity.rotation = rearranged
    entity.update_transform()
    server.update_component(entity)


def scale(server: rigatoni.Server, context, vec):
    entity = server.get_delegate(context)
    entity.scale = vec
    entity.update_transform()
    server.update_component(entity)


def delete(server: rigatoni.Server, context, *args):
    sphere = server.get_delegate(context)
    server.delete_component(sphere)
    return 0
def stop_animation(server:rigatoni.Server, context, *args):
    break_value = True
    return 0


def create_next_entity(server: rigatoni.Server, context, *args):
    """
    Create a new entity for each individual animation frame

    Parameters:
    - server (rigatoni.Server): The Rigatoni server instance where the entity will be created.
    - context: The context information for the entity creation.
    - *args: Variable number of arguments passed to the method.
        - args[0][0] (str): The file path or reference for the entity creation.
        - args[0][1] (int): The version number for each byte_server
        - args[0][2] (str): The replacement ID for the entity to be replaced
    
    Returns:
    - str: The ID of the created entity.

    Example:
    entity_id = create_next_entity(server_instance, context_info, "file_path.obj", 1, "replacement_id", "material_name")
    """
    print("here is args",args)
    file = args[0][0]
    version = args[0][1]
    replacement_id = args[0][2]
    name = "Test Sphere"
    material = server.create_component(rigatoni.Material, name="Test Material")

    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices=file.points,
        indices=file.polygons,
        normals = file.normals,
        colors = file.colors,
        index_type="TRIANGLES",
        material=material.id
    )
    byte_server_largemesh = rigatoni.ByteServer(port=version)
    patches.append(geo.build_geometry_patch(server, name, patch_info, byte_server_largemesh,generate_normals = False))
    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)
    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0, 5, 0, 0)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    entity.methods_list = [
        server.get_delegate_id("noo::set_position"),
        server.get_delegate_id("noo::set_rotation"),
        server.get_delegate_id("noo::set_scale"),
        server.get_delegate_id("stop animation"),
        server.get_delegate_id("delete"),
    ]
    server.update_component(entity)
    ### Delete previous frame
    server.delete_component(replacement_id) 
    return entity.id

def loop_scene(server: rigatoni.Server, context, *args):
    """
    Create the first frame and then loop through the rest to build a scene.
    Parameters:
    - server (rigatoni.Server): The Rigatoni server instance where the scene will be created.
    - *args: Variable number of arguments passed to the method.
        - args[0] (int): byte server port number
        - args[1] (str): The name for the initial entity.
        - args[2] (rigatoni.Material.Id): The id for the previous frame
    """
    version= 8000
    name = "Test Sphere"
    material = server.create_component(comp_type = rigatoni.Material, name="Test Material")
    # Create Patch
    patches = []
    patch_info = geo.GeometryPatchInput(
        vertices=starting_data.points,
        indices=starting_data.polygons,
        normals = starting_data.normals,
        colors = starting_data.colors,
        index_type="TRIANGLES",
        material=material.id
    )
    byte_server_largemesh = rigatoni.ByteServer(port=version)
    patches.append(geo.build_geometry_patch(server, name, patch_info, byte_server_largemesh,generate_normals = False)) 
    # Create geometry using patches
    sphere = server.create_component(rigatoni.Geometry, name=name, patches=patches)
    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0, 5, 0, 0)],
    )
    entity = geo.build_entity(server, geometry=sphere, instances=instances)
    entity.methods_list = [
        server.get_delegate_id("noo::set_position"),
        server.get_delegate_id("noo::set_rotation"),
        server.get_delegate_id("stop animation"),
        server.get_delegate_id("noo::set_scale"),
    ]
    server.update_component(entity)
    id = entity.id
    version += 1
    for file in file_data:
        if(break_value == True):
            break
        id = create_next_entity(server, context,[file, version, id])
        version += 1
    return 0


# define arg documentation for injected method
instance_args = [
    rigatoni.MethodArg(name="entity id", doc="What're you creating an instance of?", editor_hint="noo::entity_id"),
    rigatoni.MethodArg(name="position", doc="Where are you putting this instance? vec3", editor_hint="noo::array"),
    rigatoni.MethodArg(name="color", doc="What color is this instance? RGBA Vector", editor_hint="noo::array"),
    rigatoni.MethodArg(name="rotation", doc="How is this instance rotated? Vec4", editor_hint="noo::array"),
    rigatoni.MethodArg(name="scale", doc="How is this instance scaled? Vec3", editor_hint="noo::array")
]

move_args = [
    rigatoni.MethodArg(name="position", doc="Where to move to", editor_hint="noo::array")
]

rot_args = [
    rigatoni.MethodArg(name="rotation", doc="How to rotate", editor_hint="noo::array")
]

scale_args = [
    rigatoni.MethodArg(name="scale", doc="How to scale", editor_hint="noo::array")
]

# Define starting state
starting_state = [
    rigatoni.StartingComponent(rigatoni.Method, {"name": "create_animation", "arg_doc": []}, loop_scene, True),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "delete", "arg_doc": []}, delete),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "stop animation", "arg_doc": []}, stop_animation),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "noo::set_position", "arg_doc": [*move_args]}, move),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "noo::set_rotation", "arg_doc": [*rot_args]}, rotate),
    rigatoni.StartingComponent(rigatoni.Method, {"name": "noo::set_scale", "arg_doc": [*scale_args]}, scale),
]

delegates = {
    rigatoni.Entity: EntityDelegate
}

logging.basicConfig(
    format="%(message)s",
    level=logging.DEBUG
)

def main():
    global file_data, starting_data, slide_count, break_value, nood_data
    global version_num
    break_value = False
    slide_count = 0
    starting_data = threading_strainer("path/to/first/file/10.ply")

    folder_path = "path/to/folder/"
    file_data = []

    files = os.listdir(folder_path)

    ### Sort files based on number, example of file name is 00.ply, 1.ply....
    files = [file for file in files if file.endswith(".ply")]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        result = threading_strainer(file_path)
        file_data.append(result)

    server = Server(50000, starting_state, delegates)
    server.run()

if __name__ == "__main__":
    main()