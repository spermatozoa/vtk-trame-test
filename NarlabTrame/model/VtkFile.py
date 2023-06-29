import os
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
    vtkTextProperty,
)
    
class VtkFile():
    
    static_id_counter = -1    
    @staticmethod
    def getNextID():
        VtkFile.static_id_counter += 1
        return VtkFile.static_id_counter        
        
    def __init__(self, file_name:str, file_path) :
        """Initialize VtkFile

        Args:
            file_name (str): dile name of .vtk file
            file_path (absolute path to file): for VtkReader reading file
        """
        self.file_name = file_name
        self.id = VtkFile.getNextID()
        self.reader = self.setReader(file_path)
        self.vector_list = self.getVectorList(self.reader)
        self.scalar_list = self.getScalarList(self.reader)
        self.warp_vector = self.setWarpVectorFilter(self.reader)
        self.lookup_table = self.setLookUpTable()
        self.mapper = self.setMapper(self.reader, self.warp_vector, self.lookup_table)
        self.actor = self.setActor(self.mapper)
        self.state_cache = {}

    def setVisibility(self, isV):
        """actor visibility

        Args:
            isV (bool): is this vtkfile Visible
        """
        self.actor.SetVisibility(1 if isV else 0)
    
    def setReader(self, file_path):   
        """
        Args:
            file_path : string 

        Returns:
            vtkReader: vtkUnstructuredGridReader
        """
        reader = vtkUnstructuredGridReader()
        if not os.path.exists(file_path):
            raise Exception("Reader: {} not exist".format(self.file_name))
        reader.SetFileName(file_path)
        reader.ReadAllScalarsOn() # need since getpointdata().getarray() need
        reader.ReadAllVectorsOn() # same as above
        reader.Update()
        return reader
    
    def getVectorList(self, reader) -> list:   
        """

        Args:
            reader (vtkReader): to read UnstructureVtkFile

        Raises:
            Exception: no vector in file

        Returns:
            list: vector_list of vtk_file
        """
        # Set the name of the vector data to extract.
        num_vector = reader.GetNumberOfVectorsInFile()
        vector_list = []
        for i in range(num_vector):
            vector_list.append(reader.GetVectorsNameInFile(i))
        if len(vector_list) == 0:
            raise Exception("no vectors in {} -> will cause warpVector failed".format(self.file_name))
        # reader.SetVectorsName(vector_list[0])
        return vector_list
    
    def getScalarList(self, reader) -> list:
        """

        Args:
            reader (vtkReader): to read UnstructureVtkFile

        Returns:
            list: scalar_list of VtkFile
        """
        # set the name of the scalar data to extract
        num_scalar = reader.GetNumberOfScalarsInFile()
        scalar_list = []
        for i in range(num_scalar):
            scalar_list.append(reader.GetScalarsNameInFile(i))
        if len(scalar_list) == 0:
            # raise Exception("no scalars in file")
            print("warning: no scalars in file")
        return scalar_list
    
    def setWarpVectorFilter(self, reader) -> vtkWarpVector:
        """set up WarpVector

        Args:
            reader (vtkReader): to read UnstructureVtkFile

        Returns:
            vtkWarpVector: to deform model
        """
        warpVector = vtkWarpVector()
        warpVector.SetInputConnection(reader.GetOutputPort())
        # warpVector.SetScaleFactor(0)
        warpVector.Update()
        return warpVector
    
    def setLookUpTable(self) -> vtkLookupTable:
        """set up color map of model

        Returns:
            vtkLookupTable
        """
        # Mesh: Apply rainbow color map
        # Create a custom lut. The lut is used for both at the mapper and at the scalar_bar
        mesh_lut = vtkLookupTable()
        mesh_lut.SetHueRange(0.666, 0.0)
        mesh_lut.SetSaturationRange(1.0, 1.0)
        mesh_lut.SetValueRange(1.0, 1.0)
        mesh_lut.Build()
        return mesh_lut
    
    def setMapper(self, reader, warpVector, mesh_lut) -> vtkDataSetMapper:
        """set up mapper

        Args:
            reader (vtkReader): to read UnstructureVtkFile
            warpVector (vtkWarpVector): to get OututPort
            mesh_lut (vtkLookupTable): color map of model

        Returns:
            vtkDataSetMapper
        """
        scalar_range = reader.GetOutput().GetScalarRange()
        # Mesh
        mesh_mapper = vtkDataSetMapper()
        mesh_mapper.SetInputConnection(warpVector.GetOutputPort())
        mesh_mapper.SetLookupTable(mesh_lut)
        mesh_mapper.GetLookupTable().SetRange(scalar_range)
        # mesh_mapper.SetScalarRange(scalar_range)  not work
        mesh_mapper.SetUseLookupTableScalarRange(True)
        mesh_mapper.SetScalarVisibility(True)
        return mesh_mapper
        
    def setActor(self, mesh_mapper):
        """create actor (default: visibility off)

        Args:
            mesh_mapper: vtkMapper

        Returns:
            mesh_actor: vtkActor
        """
        mesh_actor = vtkActor()
        mesh_actor.SetMapper(mesh_mapper)  
        # Mesh: Setup default representation to surface
        mesh_actor.GetProperty().SetRepresentationToSurface()
        mesh_actor.GetProperty().SetPointSize(1)
        mesh_actor.GetProperty().EdgeVisibilityOff()
        # mesh_actor.GetProperty().SetRepresentationToPoints()
        # mesh_actor.GetProperty().SetPointSize(5)
        # mesh_actor.GetProperty().EdgeVisibilityOff()
        
        mesh_actor.SetVisibility(0)
        return mesh_actor

