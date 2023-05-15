from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

class VtkWindow():
    def __init__(self):
        self.colors = vtkNamedColors()
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(self.colors.GetColor3d('MediumSeaGreen')) # css3 color name
        self.render_window = vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.render_window_interactor = vtkRenderWindowInteractor()
        self.render_window_interactor.SetRenderWindow(self.render_wWindow)
        self.render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera() 
        
        self.axes_actor = vtkAxesActor()
        # print(axes.GetAxisLabels())
        self.orientation_marker_widget = self.OrientationMarker(self.axes_actor)
            
            
    # Cube Axes
    def CubeAxesActor(self, actor) -> vtkCubeAxesActor:
        cube_axes = vtkCubeAxesActor()
        self.renderer.AddActor(cube_axes)
        cube_axes.SetBounds(actor.GetBounds())
        cube_axes.SetCamera(self.renderer.GetActiveCamera())
        # cube_axes.SetXLabelFormat("%6.1f")
        # cube_axes.SetYLabelFormat("%6.1f")
        # cube_axes.SetZLabelFormat("%6.1f")
        cube_axes.SetFlyModeToOuterEdges()
        return cube_axes

    def OrientationMarker(self, axes) -> vtkOrientationMarkerWidget:
        widget = vtkOrientationMarkerWidget()
        rgba = [0] * 4
        self.colors.GetColor('Carrot', rgba)
        widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(self.render_window_interactor)
        widget.SetViewport(0.0, 0.0, 0.5, 0.5)
        widget.SetEnabled(1)
        widget.InteractiveOff()
        return widget