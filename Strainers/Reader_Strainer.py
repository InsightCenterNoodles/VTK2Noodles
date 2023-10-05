"""
Author @Jonny Bachman
Filter to read .vtp file data primtiives into NOODLEs. 
Output is an array of arrays, points and polygon indices as of 7/3/23
Support for normals and texture coordinates to be developed in the future.

Consume_faces function is based upon pywavefront's obj exporter method called consume_faces. 
This method triangulates polygons with more than 3 vertices.
Consume_faces in this file is based upon the documentation and code found here: https://github.com/pywavefront/PyWavefront/blob/master/pywavefront/obj.py

"""
import numpy as np
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtk import vtkOBJReader, vtkGLTFReader, vtkPLYReader
from VTKnamedColorsNOODLES import VTKColors
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.numpy_interface import algorithms as akgs
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch


class Properties:
    """
    Class representing properties of an object.

    Properties include points, normals, polygons, scalars, and colors.

    Attributes:
        points (list): A list to store the points of the object.
        normals (list): A list to store the normals of the object.
        polygons (list): A list to store the polygons of the object.
        scalars (list): A list to store the scalar values of the object.
        colors (list): A list to store the colors of the object.
    """
    def __init__(self):
        self.points = []
        self.normals = []
        self.polygons = []
        self.scalars = []
        self.colors = []

def noodStrainer(filename):
    """
    Reads a obj, vtp, ply, or gltf file and extracts relevant data into a custom format.
    If a different file type is needed, add the import to this strainer. 

    Args:
        filename (str): The path to the VTK XML PolyData file.

    Returns:
        data (Properties): An instance of the Properties class containing extracted data.

    Example usage:
    #reader = vtkXMLPolyDataReader()
        data = noodStrainer(/Users/jbachman/Downloads/workspace/aug4realdemo_magvort0.ply'input.vtp')
    """
    file_extension = filename[-3:]
    if file_extension == "ply":
        reader = vtkPLYReader()
    elif file_extension == "obj":
        reader = vtkOBJReader()
    elif file_extension == "vtp":
        reader = vtkXMLPolyDataReader()
    else:
        print("file type not standard, if vtk reader exists for file type, input manually")
    reader.SetFileName(filename)
    reader.Update()
    s_array = dsa.WrapDataObject(reader.GetOutput())
    #### Test area for color
    point_data = s_array.PointData
    point_data_array_names = point_data.keys()

    names_to_check = ["RGB", "RGBA", "SCALARS", "Scalars", "Scalars_"]  # Names to check

    result_dict = [0]  # Dictionary to store the names that are present in the set
    for name in names_to_check:
        if name in point_data_array_names:
            result_dict[0] = name


###Wrap the vtk data object so its data is accesible
    polygons = s_array.GetPolygons()
    point_array = []
    normals = s_array.GetPointData().GetNormals()
    num_points = len(s_array.Points)
    print("LINE 83")
    indy = 0
    ### Turn Point data into pretty format
    while (indy < num_points):
        point = s_array.Points.GetTuple(indy)
        point_array.append(point)
        indy += 1
    point_indices = []
    index = 0
    ### Turn Polygon indices into pretty format
    while index < len(polygons):
        num_vertices = polygons[index]
        polygon_vertices = polygons[index+1:index+1+num_vertices]
        point_indices.append(list(polygon_vertices))
        index += num_vertices + 1
    pointdatalength = len(s_array.PointData.keys())

    triangulated = []
    triangulated = consume_faces(point_array,point_indices)
    normal_array = []
    TCoords_array = []
    try:
        num_normals = s_array.GetPointData().GetNormals().GetNumberOfTuples()
    except Exception as e:
        print("No normals available, generate with Rigatoni")
    index1 = 0
    ### package normals
    if s_array.GetPointData().GetNormals():
        while(index1 < num_normals ):
            norm = s_array.GetPointData().GetNormals().GetTuple(index1)
            normal_array.append(norm)
            index1 += 1
    ### Turn normals into pretty format
    ### Turn T Coords into pretty format
    ### As of 9/3 this is causing weird errors and I havent encontered T coords ever so just gonna let it be. 
    try:
        if 'TCoords' in s_array.PointData:
            TCoords_array = []
            num_cords = len(s_array.PointData['TCoords'])
            index = 0
        while (index < num_cords):
            point = s_array.PointData['TCoords'].GetTuple(index)
            TCoords_array.append(point)
            index += 1
    except:
        print("No Texture Coordinates Available")
    data = Properties()
    data.points = Scale_by(point_array,0.5)
    data.polygons = triangulated
    data.normals = normal_array
    height_values = []
    for val in data.points:
        height_values.append(val[1])
    try:
        colors = s_array.PointData[result_dict[0]]
        data.colors = convert_to_0_1_scale(colors)
    except Exception as e:
        data.colors = generate_colors_for_polygons(data.points,data.polygons,height_values)
    return data


def convert_to_0_1_scale(color_data):
    """
    Converts 0-255 rgb values to 0-1 scale. 
    :param color_data: list of lists, containg color dat 0-255
    :returns correct list of lists. 
    """
    converted_data = []
    for color in color_data:
        if len(color) == 3:
            converted_color = [channel / 255.0 for channel in color]
            converted_color.append(1.0)
            converted_data.append(converted_color)
        if len(color) == 4:
            converted_color = [channel / 255.0 for channel in color]
            converted_data.append(converted_color)
    return converted_data  

def consume_faces(points, polygons):
    """
    Large part taken from pywavefront github
    Consume polygons and output triangles. May not be the most efficent way to create triangles.

    :param points: A list of points representing the vertices of the polygons.
    :param polygons: A list of polygons, where each polygon is a list of indices representing the vertices.
    :return: A list of triangles representing the polygons.
    """
    collected_faces = []  # List to store triangles

    # Helper function to append triangles
    def emit_triangle(v1, v2, v3):
        collected_faces.append([v1, v2, v3]) 
    for polygon in polygons:
        num_vertices = len(polygon)

        if num_vertices < 3:
            continue 

        # Emit the first triangle of the polygon
        v1 = polygon[0]
        v2 = polygon[1]
        v3 = polygon[2]
        emit_triangle(v1, v2, v3)

        # triangulate rest of triangles by pinning down v1 and moving through points
        for i in range(3, num_vertices):
            v_current = polygon[i]
            v_last = polygon[i - 1]
            emit_triangle(v1, v_last, v_current)

    return collected_faces


def generate_colors_for_polygons(vertices, polygons, values, cmap='cool'):
    """
    Generate Colors 

    :param vertices: a lis of polygon points
    :param polygons: A list of polygons, where each polygon is a list of indices representing the vertices.
    :param values: Values corresponding to each point, will be normalized in 0-1 range and used for coloring. Lack of values results in random coloring.
    _param cmap: matplot color map, default to inferno but can be overridden. 
    :return: A list of colors correspionding to .
    """
    if values == None:
        values = np.random.rand(len(vertices))
        print(len(values))
    else:
        # Normalize values to the range [0, 1]
        values = np.array(values)
        values = (values - values.min()) / (values.max() - values.min())
    # Create a color map
    colormap = plt.get_cmap(cmap)

    colors = []
    for val in values:
        # 9/22 subscripting is not needed for total random gen. Confused why I needed it before. 
        rgba_color = colormap(val)

        red = round(rgba_color[0],3)
        green = round(rgba_color[1],3)
        blue = round(rgba_color[2],3)

        colors.append([red, green, blue,1.0])

    return colors

def Scale_by(oldpoints,scalefactor):
    points = []
    for point in oldpoints:
        new_point = []
        i = 0
        while i < 3:
            new_one_dim = point[i] * scalefactor
            new_point.append(new_one_dim)
            i+=1
        points.append(new_point)
    return points