from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame, html
from NarlabTrame.controller.Constant import *

DEFAULT_SCALE_FACTOR = 1

class IndexPage():
    def __init__(self, server, ctrl, renderWindow, widget):
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
                self.tool_bar_icon()
            with layout.drawer as drawer:
                # drawer components
                drawer.width = 325    
                with vuetify.VExpansionPanels(
                    multiple=True,
                ):
                    self.vtk_file_selector()
                    self.warp_panel()
                    self.representation_panel()


    

    

        

