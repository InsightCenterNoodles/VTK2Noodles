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

def VTPnoodStrainer(filename):
    """
    Reads a VTK XML PolyData file and extracts relevant data into a custom format.

    Args:
        filename (str): The path to the VTK XML PolyData file.

    Returns:
        data (Properties): An instance of the Properties class containing extracted data.

    Example usage:
        data = VTPnoodStrainer('input.vtp')
    """
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    s_array = dsa.WrapDataObject(reader.GetOutput())
    print(s_array)
###Wrap the vtk data object so its data is accesible
    polygons = s_array.GetPolygons()
    point_array = []
    normals = s_array.GetPointData().GetNormals()
    num_points = len(s_array.Points)
    
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
    num_normals = s_array.GetPointData().GetNormals().GetNumberOfTuples()
    index1 = 0
    ### package normals
    if s_array.GetPointData().GetNormals():
        while(index1 < num_normals ):
            norm = s_array.GetPointData().GetNormals().GetTuple(index1)
            normal_array.append(norm)
            index1 += 1
    ### Turn normals into pretty format
    ### Turn T Coords into pretty format
    if 'TCoords' in s_array.PointData:
        TCoords_array = []
        num_cords = len(s_array.PointData['TCoords'])
        index = 0
        while (index < num_cords):
            point = s_array.PointData['TCoords'].GetTuple(index)
            TCoords_array.append(point)
            index += 1
    data = Properties()
    data.points = point_array
    data.polygons = triangulated
    data.normals = normal_array
    
    """if pointdatalength == 0:
        data.points = ["No point data given"]
    elif pointdatalength == 1:
        data.normals = normal_array
    elif pointdatalength == 2:
        data.normals = normal_array
        data.scalars = TCoords_array"""
    return data
#points_array = np.array([points.GetPoint(i) for i in range(points.GetNumberOfPoints())])
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


def generate_colors_for_polygons(vertices, polygons, values=None, cmap='inferno'):
    """
    Generate Colors 

    :param vertices: a lis of polygon points
    :param polygons: A list of polygons, where each polygon is a list of indices representing the vertices.
    :param values: Values corresponding to each point, will be normalized in 0-1 range and used for coloring. Lack of values results in random coloring.
    _param cmap: matplot color map, default to inferno but can be overridden. 
    :return: A list of colors correspionding to .
    """
    if values is None:
        values = np.random.rand(len(vertices))
    else:
        # Normalize values to the range [0, 1]
        values = np.array(values)
        values = (values - values.min()) / (values.max() - values.min())
    # Create a color map
    colormap = plt.get_cmap(cmap)

    colors = []
    for val in values:
        # Get the color for the current value from the colormap
        #subscripting 0 because random gen creates 3x as many values as needed
        rgba_color = colormap(val[0])

        red = float(rgba_color[0])
        green = float(rgba_color[1])
        blue = float(rgba_color[2])

        
        colors.append([red, green, blue])

    return colors
