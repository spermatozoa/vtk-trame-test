from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

class VtkWindow():
    def __init__(self):
        self.colors = vtkNamedColors()
        self.renderer = self.setRenderer()
        self.render_window = self.setRenderWindow(self.renderer)
        self.render_window_interactor = self.setRenderWindowInteractor(self.render_window)
        
        self.axes_actor = vtkAxesActor()
        # print(axes.GetAxisLabels())
        self.orientation_marker_widget = self.OrientationMarker(self.axes_actor, self.render_window_interactor)
        self.scalar_bar = self.setScalarBar(self.renderer)
            
            
    # Cube Axes
    def CubeAxesActor(self, actor, renderer) -> vtkCubeAxesActor:
        cube_axes = vtkCubeAxesActor()
        self.renderer.AddActor(cube_axes)
        cube_axes.SetBounds(actor.GetBounds())
        cube_axes.SetCamera(renderer.GetActiveCamera())
        # cube_axes.SetXLabelFormat("%6.1f")
        # cube_axes.SetYLabelFormat("%6.1f")
        # cube_axes.SetZLabelFormat("%6.1f")
        cube_axes.SetFlyModeToOuterEdges()
        return cube_axes

    def OrientationMarker(self, axes, render_window_interactor) -> vtkOrientationMarkerWidget:
        widget = vtkOrientationMarkerWidget()
        rgba = [0] * 4
        self.colors.GetColor('Carrot', rgba)
        widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(render_window_interactor)
        widget.SetViewport(0.0, 0.0, 0.5, 0.5)
        widget.SetEnabled(1)
        widget.InteractiveOff()
        return widget
    
    def setRenderer(self):
        renderer = vtkRenderer()
        renderer.SetBackground(self.colors.GetColor3d('MediumSeaGreen')) # css3 color name
        return renderer
    
    def setRenderWindow(self, renderer):
        render_window = vtkRenderWindow()
        render_window.AddRenderer(renderer)
        return render_window
    
    def setRenderWindowInteractor(self, render_window):
        render_window_interactor = vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)
        render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera() 
        return render_window_interactor
    
    def setScalarBar(self, renderer):        
        # create the scalar_bar
        scalar_bar = vtkScalarBarActor()       
        renderer.AddActor(scalar_bar)
        return scalar_bar
        
    def updateScalarBar(self, vtk_file):
         # scalar_bar.SetOrientationToHorizontal()
        lut = vtk_file.actor.GetMapper().GetLookupTable()
        self.scalar_bar.SetLookupTable(lut)
        self.scalar_bar.GetTitleTextProperty().SetColor(1,0,0)
        self.scalar_bar.DrawTickLabelsOn()
        self.scalar_bar.DrawAnnotationsOn()
        self.scalar_bar.SetNumberOfLabels(10)
        if vtk_file.scalar_list != []:
            self.scalar_bar.SetTitle(vtk_file.scalar_list[0])
        else:
            self.scalar_bar.SetVisibility(0)
        # textFormat = vtkTextProperty()
        # textFormat.SetFontSize(160)
        # textFormat.SetColor(1,1,1) 
        # scalar_bar.SetTitleTextProperty(textFormat)
        # scalar_bar.SetLabelTextProperty(textFormat)
        # scalar_bar.SetAnnotationTextProperty(textFormat)
    
    def addActor(self, actor):
        self.renderer.AddActor(actor)
        
    def resetCamera(self):
        self.renderer.ResetCamera()