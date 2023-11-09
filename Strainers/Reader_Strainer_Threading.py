"""
Author @Jonny Bachman
Filter to read file data into NOODLES
This filter utilizes python threading to speed up the packaging of VTK/Paraview data as fast as possible.
Requirements for this filter:
-polygons must be triangles, this can be achieved in Paraview with the triangle filter
-Normals must be generated, achieved through paraview with generate normals filter

"""
import numpy as np
import time
import sys
import threading
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtk import vtkOBJReader, vtkGLTFReader, vtkPLYReader
from vtkmodules.numpy_interface import dataset_adapter as dsa

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

        self.points = np.array([])
        self.normals = np.array([])
        self.polygons = np.array([])
        self.scalars = np.array([])
        self.colors = np.array([])

def handleColor(s_array):
    """
    Extract and process color data from the input data and store it in the 'data' object.
    Parameters: s_array: Input data, numpy wrapper
    Returns: None, assigns property of global data class
    """
    stcolor = time.time()
    point_data = s_array.PointData
    point_data_array_names = point_data.keys()
    result_dict = [0]  # Dictionary to store the names that are present in the set
        ### height values for optional coloring by height, optional
    names_to_check = ["RGB", "RGBA", "SCALARS", "Scalars", "Scalars_"]
    for name in names_to_check:
        if name in point_data_array_names:
            result_dict[0] = name
    try: 
        colors = np.array(s_array.PointData[result_dict[0]], dtype = int)
    except:
        print("no colors available")
    ### concert to_0_1 might not even be neccesary
    #finished_colors = convert_to_0_1_scale(colors)
    endcolor = time.time()
    print("Time of colors", stcolor-endcolor)
    data.colors = colors
    return

### This version assumes ParaView triangle filter is applied. 
def handlePolygons(s_array):
    """
    Processes polygon data and stores it in the data object.
    Parameters: s_array: Input data, numpy wrapper
    Returns: None, assigns data.polygons
    """
    stpp = time.time()
    polygons = np.array(s_array.GetPolygons())
    
    remainder = len(polygons) % 3
    polygons2 = polygons[:-remainder]
    point_indices = polygons2.reshape(-1,3)
    data.polygons = point_indices
# Reshape the array into a 2D array with 3 columns
    endpp = time.time()
    print("here are poly",point_indices[100])
    print("time of polys", endpp-stpp)
    return 

    """
    #### Slower Version that alters data less
    num_polygons = len(polygons)
    point_indices = np.empty((num_polygons,3), dtype = int)
    index = 0 
    while index < num_polygons:
        num_vertices = polygons[index]
        polygon_vertices = polygons[index+1:index+1+num_vertices]
        point_indices[index] = polygon_vertices
        index += num_vertices + 1
    """

def handlepoints(s_array):
    """
    Processes point data and stores it in the data object.
    Parameters: s_array: Input data, numpy wrapper
    Returns: None, assigns data.points
    """
    st = time.time()
    num_points = len(s_array.Points)
    points = np.array(s_array.Points)
    data.points = points
    end = time.time()
    print("time of points", end-st)
    return


def handleNormals(s_array):
    st_norm = time.time()
    index1 = 0
    ### package normals
    """
    try:
        num_normals = s_array.GetPointData().GetNormals().GetNumberOfTuples()
        normal_array = np.empty((num_normals,3), dtype = float)
        
    except Exception as e:
        print("No normals available, generate with Rigatoni")
    if s_array.GetPointData().GetNormals():
        while(index1 < num_normals ):
            norm = s_array.GetPointData().GetNormals().GetTuple(index1)
            normal_array[index1] = norm
            index1 += 1
    end_norm = time.time()
    data.normals = normal_array
    """
    if s_array.GetPointData().GetNormals():
        normal_array = np.array(s_array.GetPointData().GetNormals(), dtype = float)
        data.normals = normal_array
    else:
        print("no normals available")
    end_norm = time.time()
    print("time of normals", st_norm-end_norm)
    return 

### Extra Functions that can be used as needed. 
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
    :param vertices: a list of polygon points
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

def threading_strainer(filename):
    """
    Reads a obj, vtp, ply, or gltf file and extracts relevant data into a custom format.
    If a different file type is needed, add the import to this strainer. 
    This is the most efficent strainer, requires polygons to be traingles with color and normal generation completed.
    Args:
        filename (str): The path to the VTK/Paraview file.

    Returns:
        data (Properties): An instance of the Properties class containing extracted data.
    """
    global s_array
    global data
    data = Properties()
    st = time.time()
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

    t1 = threading.Thread(target=handlePolygons, args=(s_array,))
    t2 = threading.Thread(target=handleNormals, args=(s_array,))
    t3 = threading.Thread(target=handleColor, args=(s_array,))
    t4 = threading.Thread(target=handlepoints, args=(s_array,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()


    t1.join()
    t2.join()
    t3.join()
    t4.join()
    # Now, you can access the processed data properties in the 'data' object.
    et = time.time()
    print("time of program", et-st)
    return data