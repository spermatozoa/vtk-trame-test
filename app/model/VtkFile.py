from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader
from vtkmodules.vtkFiltersGeneral import (
    vtkWarpVector,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkTextProperty,
)

class VtkFile():
    def __init__(self, file_name) :
        self.file_name = file_name
        
    
    def warpVectorFilter(self, reader):
        warpVector = vtkWarpVector()
        warpVector.SetInputConnection(reader.GetOutputPort())
        # warpVector.SetScaleFactor(0)
        warpVector.Update()
        return warpVector
    
    def process_vtk_file(file_name):
    reader = vtkUnstructuredGridReader()
    if not os.path.exists(file_name):
        raise Exception("file not exist")
    reader.SetFileName(file_name)
    reader.ReadAllScalarsOn() # need since getpointdata().getarray() need
    reader.ReadAllVectorsOn() # same as above
    reader.Update()

    # Set the name of the vector data to extract.
    num_vector = reader.GetNumberOfVectorsInFile()
    vector_list = []
    for i in range(num_vector):
        vector_list.append(reader.GetVectorsNameInFile(i))
    if len(vector_list) == 0:
        raise Exception("no vectors in file")
    # reader.SetVectorsName(vector_list[0])

    # set the name of the scalar data to extract
    num_scalar = reader.GetNumberOfScalarsInFile()
    scalar_list = []
    for i in range(num_scalar):
        scalar_list.append(reader.GetScalarsNameInFile(i))
    if len(scalar_list) == 0:
        # raise Exception("no scalars in file")
        print("warning: no scalars in file")

    warpVector = warpVectorFilter(reader)


    # Mesh: Apply rainbow color map
    # Create a custom lut. The lut is used for both at the mapper and at the scalar_bar
    mesh_lut = vtkLookupTable()
    # mesh_lut = mesh_mapper.GetLookupTable()
    mesh_lut.SetHueRange(0.666, 0.0)
    mesh_lut.SetSaturationRange(1.0, 1.0)
    mesh_lut.SetValueRange(1.0, 1.0)
    mesh_lut.Build()


    scalar_range = reader.GetOutput().GetScalarRange()
    # Mesh
    mesh_mapper = vtkDataSetMapper()
    mesh_mapper.SetInputConnection(warpVector.GetOutputPort())
    mesh_mapper.SetLookupTable(mesh_lut)
    mesh_mapper.GetLookupTable().SetRange(scalar_range)
    # mesh_mapper.SetScalarRange(scalar_range)  not work
    mesh_mapper.SetUseLookupTableScalarRange(True)
    mesh_mapper.SetScalarVisibility(True)
    mesh_actor = vtkActor()
    mesh_actor.SetMapper(mesh_mapper)

    # Mesh: Setup default representation to surface
    mesh_actor.GetProperty().SetRepresentationToSurface()
    mesh_actor.GetProperty().SetPointSize(1)
    mesh_actor.GetProperty().EdgeVisibilityOff()
    # mesh_actor.GetProperty().SetRepresentationToPoints()
    # mesh_actor.GetProperty().SetPointSize(5)
    # mesh_actor.GetProperty().EdgeVisibilityOff()
    return mesh_actor, scalar_list, reader, vector_list, warpVector
