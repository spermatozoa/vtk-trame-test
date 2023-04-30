import os
from enum import Enum
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame, html

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
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

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

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--base-dir", help="Directory to vtk files", dest="dir", required=True)
args = parser.parse_args()
# print(args.directory)

def get_sub_dir_file(root_dir):
    if not root_dir:
        raise Exception("Base dir should not be empty")
    sub_dir_files = {}
    sub_dir_list = []
    for item in os.listdir(root_dir):
        sub_path = os.path.join(root_dir, item)
        if os.path.isdir(sub_path):
            sub_dir_list.append(item)
            file_list = []
            for f in os.listdir(sub_path):
                f_path = os.path.join(sub_path, f)
                if os.path.isfile(f_path):
                    file_list.append(f)
                elif os.path.isdir(f_path):
                    print("there is dir in ", sub_path)
            sub_dir_files[item] = file_list
        elif os.path.isfile(sub_path):
            print("there is file in ", root_dir)        
    if not sub_dir_list:
        raise Exception("no sub dir")
    elif not sub_dir_files:
        raise Exception("no file in sub dir")
    return sub_dir_list, sub_dir_files
root_dir = args.dir
sub_dir_list, sub_dir_files = get_sub_dir_file(root_dir)
cur_sub_dir_idx = 0
cur_file_idx = 0

def getVtkFileName(sub_dir_idx=0, file_idx=0, id=-1):
    if id != -1:
        for key, val in vtk_file_dict.items():
            if val['id'] == id:
                return key
    return sub_dir_files[sub_dir_list[sub_dir_idx]][file_idx]
def getVtkFilePath(sub_dir_idx, file_idx):
    return os.path.join(root_dir, sub_dir_list[sub_dir_idx], getVtkFileName(sub_dir_idx, file_idx))

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

class Orientation(Enum):
    pos_z = 0
    pos_y = 1
    pos_x = 2
    neg_z = 3
    neg_y = 4
    neg_x = 5


# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------


colors = vtkNamedColors()
renderer = vtkRenderer()
renderer.SetBackground(colors.GetColor3d('MediumSeaGreen')) # css3 color name
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

def warpVectorFilter(reader):
    warpVector = vtkWarpVector()
    warpVector.SetInputConnection(reader.GetOutputPort())
    # warpVector.SetScaleFactor(0)
    warpVector.Update()
    return warpVector

# Cube Axes
def CubeAxesActor(mesh_actor):
    cube_axes = vtkCubeAxesActor()
    renderer.AddActor(cube_axes)
    # Cube Axes: Boundaries, camera, and styling
    cube_axes.SetBounds(mesh_actor.GetBounds())
    cube_axes.SetCamera(renderer.GetActiveCamera())
    # cube_axes.SetXLabelFormat("%6.1f")
    # cube_axes.SetYLabelFormat("%6.1f")
    # cube_axes.SetZLabelFormat("%6.1f")
    cube_axes.SetFlyModeToOuterEdges()

def OrientationMarker():
    axes = vtkAxesActor()
    axes.AxisLabelsOn()
    # print(axes.GetAxisLabels())

    widget = vtkOrientationMarkerWidget()
    rgba = [0] * 4
    colors.GetColor('Carrot', rgba)
    widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
    widget.SetOrientationMarker(axes)
    widget.SetInteractor(renderWindowInteractor)
    widget.SetViewport(0.0, 0.0, 0.5, 0.5)
    widget.SetEnabled(1)
    widget.InteractiveOff()
    return widget

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

    
# file_name = os.path.join(CURRENT_DIRECTORY, "linking_rod.vtk")  # minimal example vtk file
# file_name = getVtkFilePath(cur_sub_dir_idx, cur_file_idx)
vtk_file_dict = {}
init = True
tmp_id = 0
for sub_dir_name, file_list in sub_dir_files.items():
    for f in file_list:
        file_name = os.path.join(root_dir, sub_dir_name, f)
        actor, scalar_list, reader, vector_list, warp_vector = process_vtk_file(file_name)
        if init: 
            actor.SetVisibility(1)
            init = False
        else: 
            actor.SetVisibility(0)
        vtk_file_dict[f] = {'id': tmp_id,
                            'actor':actor, 
                            'scalar_list':scalar_list,
                            'reader': reader,
                            'vector_list':vector_list,
                            'warp_vector':warp_vector,
                            }
        tmp_id += 1
        renderer.AddActor(actor)

# create the scalar_bar
scalar_bar = vtkScalarBarActor()
# scalar_bar.SetOrientationToHorizontal()
first_vtk = vtk_file_dict[getVtkFileName(0,0)]
lut = first_vtk['actor'].GetMapper().GetLookupTable()
scalar_bar.SetLookupTable(lut)
scalar_bar.GetTitleTextProperty().SetColor(1,0,0)
scalar_bar.DrawTickLabelsOn()
scalar_bar.DrawAnnotationsOn()
scalar_bar.SetNumberOfLabels(10)
if first_vtk['scalar_list'] != []:
    scalar_bar.SetTitle(first_vtk['scalar_list'][0])
else:
    scalar_bar.SetVisibility(0)
# textFormat = vtkTextProperty()
# textFormat.SetFontSize(160)
# textFormat.SetColor(1,1,1) 
# scalar_bar.SetTitleTextProperty(textFormat)
# scalar_bar.SetLabelTextProperty(textFormat)
# scalar_bar.SetAnnotationTextProperty(textFormat)
renderer.AddActor(scalar_bar)

widget = OrientationMarker()

# mesh_actor.SetOrigin(0,0,0)
# mesh_actor.SetOrientation(0, 0, 180)
# mesh_actor.RotateX(-90)
# mesh_actor.RotateZ(-90)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()

state, ctrl = server.state, server.controller

state.sub_dir_list = sub_dir_list
state.cur_sub_dir_idx = cur_sub_dir_idx
state.cur_vtk_id = 0

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

# @state.change("color_name")
# def change_bg_color(color_name, **kwargs):
#     renderer.SetBackground(colors.GetColor3d(color_name))
#     ctrl.view_update()

# @state.change("actor_orientation")
def update_actor_orientation(*args, **kwargs):
    pass
    # print("args: ", type(args[0]))
    # actor_orientation = args[0]
    # if actor_orientation == Orientation.pos_x.value:
    #     print("rotate 2")
    #     renderWindow.EraseOff()
    #     mesh_actor.RotateZ(60)
    #     renderWindow.Render()
    #     renderWindow.Render()
    #     renderWindow.EraseOn()
    #     # mesh_actor.RotateX(-90)
    #     # mesh_actor.RotateZ(90)
    # elif actor_orientation == Orientation.pos_y.value:
    #     mesh_actor.SetOrientation(90, 0, 0)
    # elif actor_orientation == Orientation.pos_z.value: 
    #     mesh_actor.SetOrientation(0, 180, 0)
    # elif actor_orientation == Orientation.neg_x.value:
    #     mesh_actor.RotateX(-90)
    #     mesh_actor.RotateZ(-90)
    # elif actor_orientation == Orientation.neg_y.value:
    #     mesh_actor.SetOrientation(90, 0, 180)
    # elif actor_orientation == Orientation.neg_z.value:  
    #     mesh_actor.SetOrientation(0, 0, 0)
    # else:
    #     print("how")

    # # ctrl.view_reset_camera()
    # ctrl.view_update()

@state.change("cube_axes_visibility")
def update_cube_axes_visibility(cube_axes_visibility, **kwargs):
    # cube_axes.SetVisibility(cube_axes_visibility)
    ctrl.view_update()

@state.change("warp_vector_idx")
def update_warp_vector(warp_vector_idx, **kwargs):
    cur_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
    cur_vtk['reader'].SetVectorsName(cur_vtk['vector_list'][warp_vector_idx])
    ctrl.view_update()

@state.change("scale_factor")
def update_scale_factor(scale_factor, **kwargs):
    cur_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
    cur_vtk['warp_vector'].SetScaleFactor(scale_factor)
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
    cur_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
    property = cur_vtk['actor'].GetProperty()
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
    cur_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
    lut = cur_vtk['actor'].GetMapper().GetLookupTable()
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
    cur_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
    scalar_list = cur_vtk['scalar_list']
    reader = cur_vtk['reader']
    if len(scalar_list) > 0:
        scalar_bar.SetTitle(scalar_list[color_array_idx])
        reader.SetScalarsName(scalar_list[color_array_idx])
        reader.Update()  # Needed because of GetScalarRange
        scalar_range = reader.GetOutput().GetScalarRange()    
        mapper = cur_vtk['actor'].GetMapper()    
        # mapper.SetScalarRange(scalar_range)  not work
        mapper.GetLookupTable().SetRange(scalar_range)
        mapper.SetScalarVisibility(True)
        mapper.SetUseLookupTableScalarRange(True)
        ctrl.view_update()

@state.change("sub_dir_index","file_index")
def update_sub_dir_index(sub_dir_index=cur_sub_dir_idx, file_index=cur_file_idx, **kwargs):
    # check if variable exist (getserver() before create global variable will need to check this)
    global cur_sub_dir_idx
    global cur_file_idx
    print("sub_dir: ", sub_dir_index)
    print("file: ", file_index)
    def change_actor():
        old_vtk = vtk_file_dict[getVtkFileName(cur_sub_dir_idx, cur_file_idx)]
        new_vtk = vtk_file_dict[getVtkFileName(sub_dir_index, file_index)]
        old_vtk['actor'].SetVisibility(0)            
        new_vtk['actor'].SetVisibility(1)
        
        if new_vtk['scalar_list'] == []:
            scalar_bar.SetVisibility(0)
        else:
            lut = new_vtk['actor'].GetMapper().GetLookupTable()
            scalar_bar.SetLookupTable(lut)
            scalar_bar.SetTitle(new_vtk['scalar_list'][0])
            scalar_bar.SetVisibility(1)
        
        state.cur_vtk_id = new_vtk['id']
    try:
        if cur_sub_dir_idx == sub_dir_index:
            if cur_file_idx == file_index:
                return
            else:
                change_actor()
                cur_file_idx = file_index
        else:
            change_actor()
            cur_sub_dir_idx = sub_dir_index
            state.cur_sub_dir_idx = cur_sub_dir_idx
            cur_file_idx = 0
    except NameError:
        print("NameError")
        return
    # reader.SetFileName(getVtkFilePath(cur_sub_dir_idx, cur_file_idx))
    # reader.Update()
    ctrl.view_update()
# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

def tool_bar_icon():
    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-backup-restore")
    # vuetify.VBtn(
    #     "+X",
    #     variant="tonal",
    #     click=(update_actor_orientation, "[2]")
    # )
    vuetify.VCheckbox(
        v_model=("cube_axes_visibility", True),
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
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
        # for i in range(len(vtk_file_dict)): 
        #     vuetify.VSelect(
        #         # WarpVector
        #         # v_if=(f"{i}==cur_file_id",),
        #         v_model=("warp_vector_idx", 0),
        #         items=(
        #             f"{i}vectors",
        #             [{"text": vector_name, "value": idx} for idx, vector_name in enumerate(vtk_file_dict[getVtkFileName(id=i)]['vector_list'])],
        #         ),
        #         label="WarpVector",
        #         # value=vector_list[0],
        #         hide_details=True,
        #         dense=True,
        #         outlined=True,
        #         classes="pt-1",
        #     )
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
                # vuetify.VTextField(
                # # color
                # "color",
                # v_model=("color_name", "white"),
                # hint="color",
                # persistent_hint=True,
                # # hide_details=True, against hint so diable
                # variant="plain",
                # dense=True,
                # classes="mt-1",
                # )
            
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
                for i in range(len(vtk_file_dict)):
                    vuetify.VSelect(
                        # Color By
                        v_show=(f"{i}==cur_vtk_id"),
                        label="Color by",
                        v_model=("color_array_idx", 0),
                        items=(f"array_list{i}", 
                            [{"text": s, "value": i} for i, s in enumerate(vtk_file_dict[getVtkFileName(id=i)]['scalar_list'])],
                        ),
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

def vtk_file_chooser():
    with vuetify.VSlideGroup(v_model=("sub_dir_index",0), show_arrows=True, mandatory=True, classes="mt-2"):
        with vuetify.VSlideItem(v_for=("dir in sub_dir_list",), key=("dir",), v_slot="{ active, toggle }"):
            vuetify.VBtn(
                "{{ dir }}",
                classes="mx-2 mb-1",
                input_value=("active",),
                active_class="primary",
                rounded=True,
                click="toggle"
            )

    for i in range(len(sub_dir_list)):   
        # print(sub_dir_files[sub_dir_list[i]])         
        s = vuetify.VSelect(
            # FileSelect
            v_if=(f"{i}==cur_sub_dir_idx",),
            v_model=("file_index", 0),
            items=(
                f"files{i}",
                [{"text": file_name, "value": idx} for idx, file_name in enumerate(sub_dir_files[sub_dir_list[i]])],
            ),
            label="vtkFile",
            # value=vector_list[0],
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
            ctrl.view_widgets_set = view.set_widgets
            view.set_widgets([widget])  # or at constructor

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
            vtk_file_chooser()
            warp_panel()
            representation_panel()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
