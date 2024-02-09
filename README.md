# VTK2Noodles
This is a filter set is desgined to integrate the Visualization Tool Kit (VTK) and Paraview visualization pipelines into NOODLES. This filter set should be implemented in the creation of a Rigatoni Server as part of a custom method. Further work to develop these filters is ongoing.

## Examples
### Example 1, Paraview2Noodles
In this example, AMR data is processed in Paraview, written as .ply files for each frame and processed into Noodles.
The rigatoni server file and paraview python script is in the Paraview2Noodles folder and utilizes the Threading strainer to port the data into Noodles. Complex animations result in slower FPS, but at about the same rate as Paraview.
#### Frame rate is a faster than displayed here

![Video](https://github.com/InsightCenterNoodles/VTK2Noodles/blob/main/magvortcontourgitclip.mov)
![Video](https://github.com/InsightCenterNoodles/VTK2Noodles/blob/main/paraview2noodles.mov)

### Example 2, VTP file Strainer
In this example, medical data of two patients (one dataset of a thoracic aorta, and another of the abdominal aorta including some parts of the iliacs) was combined, visualized and stored as a .vtp file, found here: https://simtk.org/frs/?group_id=31. VTPnoodStrainer returns the points and polygons of this data. Further work to access color and process larger vtp files is ongoing.

```python
### Code adapted from Alex Racape's Rigatoni-main/tests/examples/geometry_server.py
def create_aorta(server: rigatoni.Server, context, *args):
    """Method to read .vtp files into NOODLES"""

    name = "Aorta"
    material = server.create_component(rigatoni.Material, name="Test Material")

    data = []
    data = VTPnoodStrainer("virtual_aorta_1.vtp")

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
    cylinder = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(1, 1, 1, 1)],
        colors=[(148, 0, 211)],
    )
    entity = geo.build_entity(server, geometry=cylinder, instances=instances)

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
```
### Output

![Aorta](https://github.com/InsightCenterNoodles/VTK2Noodles/assets/135997381/ff7c76a2-ff79-40b3-b63a-9bda3145bf70)


#### Second Example:
This is another example of reader strainer implemented with real data. The server method creation is exactly the same as the aorta. The polygon is combustion data of an internal combustion cylinder from the Exascale Computing Project. The client used in this example is Orzo, and serves up a 1:1 paraview scene. 

![Combustion Data](https://github.com/InsightCenterNoodles/VTK2Noodles/blob/main/orzo_paraview.png)
![Paraview ScreenShot](https://github.com/InsightCenterNoodles/VTK2Noodles/blob/main/paraviewsnap.png)

### Example 3, Basic VTK Building blocks, Source Strainer
In this example, we use "VtkNoodlesSourceStrainer.py" to access the data primitives of a cylinder vtk source object.
The output of SourceStrainer(source) is a list that contains four arrays, 0: Points 1. Polygon indices 2. Normals (if they exist) 3. Texture coordinates (if they exist). These data primtives are then used in patch creation. s
This example method **create_cylinder(server: rigatoni.Server, context, *args):** requires Rigatoni, Penne and NOODLEs explorer to be viewed properly.



```python
### Code adapted from Alex Racape's Rigatoni-main/tests/examples/geometry_server.py
def create_cylinder(server: rigatoni.Server, context, *args):
    """Test method to create 1 cylinder"""

    name = "Test Cylinder"
    material = server.create_component(rigatoni.Material, name="Test Material")

    source = vtkCylinderSource()
    source.SetRadius(0.5)
    source.SetHeight(3)
    source.SetResolution(40)
    source.Update()
    
    data = []
    data = SourceStrainer(source)

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
    cylinder = server.create_component(rigatoni.Geometry, name=name, patches=patches)

    # Set instances and create an entity
    instances = geo.create_instances(
        positions=[(0, 0, 0, 0)],
        colors=[(0, 204, 0)],
    )
    entity = geo.build_entity(server, geometry=cylinder, instances=instances)

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
```
### Output
![Image 7-10-23 at 1 02 PM](https://github.com/InsightCenterNoodles/VTK2Noodles/assets/135997381/a3fc4612-42a3-401d-b088-8883b5304486)

## Built With
* [VTK](https://github.com/Kitware/VTK)

## Authors

* **Jonny Bachman** - *Initial work* - [paulcena2](https://github.com/paulcena2)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
This filter set supports the work done by Nicholas Brunhart-Lupo (NOODLES, Penne, etc..) and Alex Racap
