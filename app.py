import os
from enum import Enum
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame, html

from vtkmodules.vtkCommonDataModel import vtkDataObject
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
)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

DEFAULT_SCALE_FACTOR = 1
CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

actor_list=[]
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

class Representation(Enum):
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


class ColorLookupTable(Enum):
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

reader = vtkUnstructuredGridReader()
file_name = os.path.join(CURRENT_DIRECTORY, "linking_rod.vtk")  # minimal example vtk file
if not os.path.exists(file_name):
    raise Exception("file not exist")
reader.SetFileName(file_name)
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
    raise Exception("no scalars in file")

def warpVectorFilter(reader):
    warpVector = vtkWarpVector()
    warpVector.SetInputData(reader.GetOutput())
    # warpVector.SetScaleFactor(0)
    warpVector.Update()
    return warpVector
warpVector = warpVectorFilter(reader)

# warp_mapper = vtkDataSetMapper()
# warp_mapper.SetInputConnection(warpVector.GetOutputPort())
# warp_actor = vtkActor()
# warp_actor.SetMapper(warp_mapper)
# actor_list.append(warp_actor)


# Extract Array/Field information
dataset_arrays = []
fields = [
    (reader.GetOutput().GetPointData(), vtkDataObject.FIELD_ASSOCIATION_POINTS),
    (reader.GetOutput().GetCellData(), vtkDataObject.FIELD_ASSOCIATION_CELLS),
]
for field in fields:
    field_arrays, association = field
    for i in range(field_arrays.GetNumberOfArrays()):
        array = field_arrays.GetArray(i)
        array_range = array.GetRange()
        dataset_arrays.append(
            {
                "text": array.GetName(),
                "value": i,
                "range": list(array_range),
                "type": association,
            }
        )
print(dataset_arrays)
default_array = dataset_arrays[0]
default_min, default_max = default_array.get("range")

# Mesh
mesh_mapper = vtkDataSetMapper()
mesh_mapper.SetInputConnection(warpVector.GetOutputPort())
mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
actor_list.append(mesh_actor)

# Mesh: Setup default representation to surface
mesh_actor.GetProperty().SetRepresentationToSurface()
mesh_actor.GetProperty().SetPointSize(1)
mesh_actor.GetProperty().EdgeVisibilityOff()
# mesh_actor.GetProperty().SetRepresentationToPoints()
# mesh_actor.GetProperty().SetPointSize(5)
# mesh_actor.GetProperty().EdgeVisibilityOff()

# Mesh: Apply rainbow color map
mesh_lut = mesh_mapper.GetLookupTable()
mesh_lut.SetHueRange(0.666, 0.0)
mesh_lut.SetSaturationRange(1.0, 1.0)
mesh_lut.SetValueRange(1.0, 1.0)
mesh_lut.Build()

# Mesh: Color by default array
mesh_mapper.SelectColorArray(default_array.get("text"))
mesh_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    mesh_mapper.SetScalarModeToUsePointFieldData()
else:
    mesh_mapper.SetScalarModeToUseCellFieldData()
mesh_mapper.SetScalarVisibility(True)
mesh_mapper.SetUseLookupTableScalarRange(True)


for actor in actor_list:
    renderer.AddActor(actor)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

@state.change("warp_vector_idx")
def update_warp_vector(warp_vector_idx, **kwargs):
    reader.SetVectorsName(vector_list[warp_vector_idx])
    ctrl.view_update()

@state.change("scale_factor")
def update_scale_factor(scale_factor, **kwargs):
    warpVector.SetScaleFactor(scale_factor)
    # print("set scale factor: ", scale_factor)
    ctrl.view_update()

def reset_scale_factor():
    state.scale_factor = DEFAULT_SCALE_FACTOR

@state.change("scale_factor_max")
def update_scale_factor_max(scale_factor_max, **kwargs):
    if not isinstance(scale_factor_max, str):
        state.scale_factor = scale_factor_max
    elif scale_factor_max.isdigit():
        state.scale_factor = int(scale_factor_max)
    else: 
        state.scale_factor = float(scale_factor_max)

@state.change("representation_mode")
def update_representation(representation_mode, **kwargs):
    property = actor_list[0].GetProperty()
    if representation_mode == Representation.Points.value:
        property.SetRepresentationToPoints()
        property.SetPointSize(5)
        property.EdgeVisibilityOff()
    elif representation_mode == Representation.Wireframe.value:
        property.SetRepresentationToWireframe()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif representation_mode == Representation.Surface.value:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif representation_mode == Representation.SurfaceWithEdges.value:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOn()
    ctrl.view_update()

@state.change("color_map")
def update_colormap(color_map, **kwargs):
    lut = actor_list[0].GetMapper().GetLookupTable()
    if color_map == ColorLookupTable.Rainbow.value:
        lut.SetHueRange(0.666, 0.0)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
    elif color_map == ColorLookupTable.Inverted_Rainbow.value:
        lut.SetHueRange(0.0, 0.666)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
    elif color_map == ColorLookupTable.Greyscale.value:
        lut.SetHueRange(0.0, 0.0)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetValueRange(0.0, 1.0)
    elif color_map == ColorLookupTable.Inverted_Greyscale.value:
        lut.SetHueRange(0.0, 0.666)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetValueRange(1.0, 0.0)
    lut.Build()
    ctrl.view_update()

@state.change("color_array_idx")
def update_color_by_name(color_array_idx, **kwargs):
    array = dataset_arrays[color_array_idx]
    _min, _max = array.get("range")
    mapper = actor.GetMapper()
    mapper.SelectColorArray(array.get("text"))
    mapper.GetLookupTable().SetRange(_min, _max)
    # if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    #     mesh_mapper.SetScalarModeToUsePointFieldData()
    # else:
    #     mesh_mapper.SetScalarModeToUseCellFieldData()
    mapper.SetScalarVisibility(True)
    mapper.SetUseLookupTableScalarRange(True)
    ctrl.view_update()
# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

def tool_bar_icon():
    vuetify.VCheckbox(
        v_model="$vuetify.theme.dark",
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    # vuetify.VCheckbox(
    #     v_model=("viewMode", "local"),
    #     on_icon="mdi-lan-disconnect",
    #     off_icon="mdi-lan-connect",
    #     true_value="local",
    #     false_value="remote",
    #     classes="mx-1",
    #     hide_details=True,
    #     dense=True,
    # )
    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-backup-restore")

def drawer_panels(panel_header):
    with vuetify.VExpansionPanel():
        vuetify.VExpansionPanelHeader(
            panel_header,
            classes="grey lighten-1 my-auto py-1 grey--text text--darken-3",
            # style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=False,
        )
        content = vuetify.VExpansionPanelContent(classes="py-2")
    return content

def warp_panel():
    with drawer_panels(panel_header="WarpVector"):
        vuetify.VSelect(
            # WarpVector
            v_model=("warp_vector_idx", 0),
            items=(
                "vectors",
                [{"text": vector_name, "value": idx} for idx, vector_name in enumerate(vector_list)],
            ),
            label="WarpVector",
            # value=vector_list[0],
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol():
                vuetify.VSlider(
                # ScaleFactor
                v_model=("scale_factor", DEFAULT_SCALE_FACTOR),
                min=0,
                max=("scale_factor_max",3000),
                step=0.01,
                # label="ScaleFactor",
                classes="mt-1",
                hide_details=True,
                dense=True,
                )            
            with vuetify.VCol(cols="4"):
                vuetify.VTextField(
                # display ScaleFactor
                "ScaleFactor",
                v_model=("scale_factor", DEFAULT_SCALE_FACTOR),
                type="number",
                hint="ScaleFactor",
                persistent_hint=True,
                # hide_details=True, against hint so diable
                variant="plain",
                dense=True,
                readonly=True,
                classes="mt-1",
                )
            
        with vuetify.VRow(classes="pt-2", dense=True):
            vuetify.VTextField(
            # set ScaleFactorMax
            "ScaleFactorMax",
            v_model=("scale_factor_max",3000),
            type="number",
            label="set ScaleFactorMax",
            placeholder="type number",
            hide_details=True,
            outlined=True,
            dense=True,
            )
            with vuetify.VBtn(icon=True, click=reset_scale_factor):
                vuetify.VIcon("mdi-restore")

def representation_panel():
     with drawer_panels(panel_header="Representation"):
        vuetify.VSelect(
            v_model=("representation_mode", Representation.Surface.value),
            items=(
                "representations",
                [{"text": r.name, "value": r.value} for r in Representation],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                    label="Color by",
                    v_model=("color_array_idx", 0),
                    items=("array_list", dataset_arrays),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    v_model=("color_map", ColorLookupTable.Rainbow.value),
                    items=(
                        "colormaps",
                        [{"text": color.name, "value": color.value} for color in ColorLookupTable],
                    ),
                    label="ColorMap",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )

        
with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Trame Example")

    with layout.root:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk.VtkLocalView(renderWindow)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        tool_bar_icon()
    with layout.drawer as drawer:
        # drawer components
        drawer.width = 325    
        with vuetify.VExpansionPanels(
            multiple=True,
        ):
            warp_panel()
            representation_panel()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
