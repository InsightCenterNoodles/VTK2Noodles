import vtk
from VTKnamedColorsNOODLES import VTKColors
from vtk import vtkTriangleFilter, vtkPolyDataMapper, vtkPolyDataNormals, vtkStaticCleanPolyData
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
def mapperStrainer(mapper):
    """
    NOODLES strainer to access vtk data primitives. 
    Provides a data list to be used in the creation of a rigatoni custom method.
    
    Parameters
    ----------
    mapper: vtkPolyDataMapper
    The provided mapper should be updated before calling this strainer.

    Returns 
    ----------
    data: list of 4 lists
    list 0: vertices
    list 1: polygons (in index format correpsonding to vertices)
    list 2: normals
    list 3: scalars (if they exist)
    """
    data = Properties()
    mapper.Update()
    # Access the polydata
    polyData = mapper.GetInput()
    if polyData == None:
        errormessage("No polydata provided, try updating mapper before passing through the filter")
    #check if polygons exist in the provided data
    connect = polyData.GetPolys().GetConnectivityArray().GetNumberOfTuples()
    if connect == 0:
        ###Throw visual error code.
        errormessage("Provided .polydata has no polygons") 
    #Run data through filtering process
    completeData = cleanData(triangulate(makeNormals(polyData)))
    #Access vertices
    vertices = GetPoints(completeData)
    pointDataholder = []
    pointDataholder = AccessPointData(completeData)
    normals = pointDataholder[0]
    scalars = pointDataholder[1]
    polygons = getPolygons(completeData)
    data = Properties()
    data.points = vertices
    data.polygons = polygons
    data.normals = normals
    data.scalars = scalars
    return data

def makeNormals(polydata):
    """
    Passes input polydata through vtk make normals filter. 

    Parameters
    ----------
    polydata: vtkPolyData

    Returns 
    ----------
    polydata that contains normal data.
    """
    normalMaker = vtkPolyDataNormals()
    normalMaker.SetInputData(polydata)
    normalMaker.Update()
    normalPolydata = normalMaker.GetOutput()
    return normalPolydata

    #Triangulate data
def triangulate(polydata):
    """
    Passes input polydata through vtk triangulation filter. 

    Parameters
    ----------
    polydata: vtkPolyData

    Returns 
    ----------
    polydata that contains triangulated polygons.
    Polygons are available in the connectivity and offsets arrays. 
    """
    Tryifyoucan = vtkTriangleFilter()
    Tryifyoucan.SetInputData(polydata)
    Tryifyoucan.Update()
    triPolydata= Tryifyoucan.GetOutput()
    return triPolydata

    # Clean the data (merge duplicate points, and/or remove unused points and/or remove degenerate cells)
def cleanData(polydata):
    """
    Passes input polydata through vtkStaticClean filter.
    Static Clean does the following tasks: merge duplicate points, and/or remove unused points and/or remove degenerate cells
    Static clean is chosen due to its suitability with large datasets
    Parameters
    ----------
    polydata: vtkPolyData

    Returns 
    ----------
    cleaned polydata, as the last step it is denoted 'completePolydata'
    """
    cleaner = vtkStaticCleanPolyData()
    cleaner.SetInputData(polydata)
    cleaner.Update()
    completePolydata = cleaner.GetOutput()

    return completePolydata

def GetPoints(completePolydata):
    """
    Access the vertices of the comepletePolydata
    Parameters
    ----------
    completePolydata: normalized, triangulated and cleaned vtkPolyData

    Returns 
    ----------
    vertices: list containing points
    """
    vertices = []
    points = completePolydata.GetPoints()
    numPoints = points.GetNumberOfPoints()
    for i in range(numPoints):
        point = points.GetPoint(i)
        vertices.append(point)
    return vertices

def AccessPointData(completePolydata):
    """
    Access the pointdata of the comepletePolydata
    This should be generalized for all polydata, if not, customization of GetArray("array_name") will be needed and user dependent
    
    Parameters
    ----------
    completePolydata: normalized, triangulated and cleaned vtkPolyData

    Returns 
    ----------
    pointdata: list with 2 lists
    list 0: normals, if they exist
    list 1: scalars, if they exist
    """
    normals = []
    scalars = []
    pointData = completePolydata.GetPointData()

    # In theory this should be generalized for all polydata, if not, customization of GetArray will be needed and user dependent
    if pointData.GetArray("Normals"):
        normalsArray = pointData.GetArray("Normals")
        numNormals = normalsArray.GetNumberOfTuples()
        for i in range(numNormals):
            normal = normalsArray.GetTuple(i)
            normals.append(normal)
    
    if pointData.GetScalars:
        scalarsArray = pointData.GetScalars
        numScalars = scalarsArray.GetNumberOfTuples()
        for i in range(numScalars):
            scalar = scalarsArray.GetTuple(i)
            scalars.append(scalar)
    pointdata = [0,0]
    pointdata[0] = normals
    pointdata[1] = scalars
    return pointdata


def getPolygons(completePolydata):
    """
    Access the polygons of the comepletePolydata
    Due to triangulation, offset array is not used. 
    Each triangle has it points stored in a sequential triple in connectivity array so offsets are not needed.
    
    Parameters
    ----------
    completePolydata: normalized, triangulated and cleaned vtkPolyData

    Returns 
    ----------
    polygons: list containing indices of polygons that correlate with vertices []
    """
    polygons = []
    # Access the polygons through connectivity and offsets.
    polys = completePolydata.GetPolys()
    polyArray = polys.GetConnectivityArray()
    offsetArray = polys.GetOffsetsArray()
    numPolys = polyArray.GetNumberOfTuples() 
    numOffsets = offsetArray.GetNumberOfTuples()

    # fill in polygons list, because we already triangulated everything we dont need to use the offsets
    # If you are using this with polygons other than triangles, the offset arrays 
    for i in range(numPolys - 3):
        polygon1 = polyArray.GetTuple(0+ i)[0]
        polygon2 = polyArray.GetTuple(1+ i)[0]
        polygon3 = polyArray.GetTuple(2+ i)[0]
        complete = []
        complete.append(polygon1)
        complete.append(polygon2)
        complete.append(polygon3)
        polygons.append(complete)
    return polygons

def errormessage(string):
    """
    Error message to display in noodles as text.
    In the future this will be a text source to display in noodles explorer
    """
    print(string)
