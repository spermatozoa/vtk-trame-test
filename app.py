import os
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

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
reader.SetVectorsName(reader.GetVectorsNameInFile(0))

warpVector = vtkWarpVector()
warpVector.SetInputData(reader.GetOutput())
# warpVector.SetScaleFactor(0)
warpVector.Update()

mapper = vtkDataSetMapper()
mapper.SetInputConnection(warpVector.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)

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


@state.change("scale_factor")
def update_scale_factor(scale_factor, **kwargs):
    warpVector.SetScaleFactor(scale_factor)
    # print("set scale factor: ", scale_factor)
    ctrl.view_update()


def reset_scale_factor():
    state.scale_factor = DEFAULT_SCALE_FACTOR


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.title.set_text("Warp Vector Example")

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
        vuetify.VSlider(
            v_model=("scale_factor", DEFAULT_SCALE_FACTOR),
            min=0,
            max=3000,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )
        with vuetify.VBtn(icon=True, click=reset_scale_factor):
            vuetify.VIcon("mdi-restore")

        vuetify.VDivider(vertical=True, classes="mx-2")

        vuetify.VSwitch(
            v_model="$vuetify.theme.dark",
            hide_details=True,
            dense=True,
        )
        with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
            vuetify.VIcon("mdi-crop-free")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
