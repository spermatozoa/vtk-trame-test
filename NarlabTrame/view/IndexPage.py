from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame, html
from NarlabTrame.controller.Constant import *
from NarlabTrame.view.Pages import Panels, ToolBarIcon, VtkFileSelector

DEFAULT_SCALE_FACTOR = 1

class IndexPage():
    def __init__(self, web_server, renderWindow, widget, ):
        """_summary_

        Args:
            web_server (WebServer): to get all useful info for settin UI
            renderWindow (vtkRenderWindow): set up vtkLocalView
            widget (VtkWidget): currently use to add orientation_marker_widget to vtkLocalView
        """
        with SinglePageWithDrawerLayout(web_server.server) as layout:
            layout.title.set_text("Trame Example")

            with layout.root:
                with vuetify.VContainer(
                    fluid=True,
                    classes="pa-0 fill-height",
                ):
                    view = vtk.VtkLocalView(renderWindow)
                    ctrl = web_server.server.controller
                    ctrl.view_update = view.update
                    ctrl.view_reset_camera = view.reset_camera
                    ctrl.view_widgets_set = view.set_widgets
                    view.set_widgets([widget])  # or at constructor

            with layout.toolbar:
                vuetify.VSpacer()
                vuetify.VDivider(vertical=True, classes="mx-2")
                ToolBarIcon.tool_bar_icon()
            with layout.drawer as drawer:
                # drawer components
                drawer.width = 325    
                with vuetify.VExpansionPanels(
                    multiple=True,
                ):
                    VtkFileSelector.vtk_file_chooser(web_server.sub_dir_list, web_server.vtk_files_dict)
                    Panels.warp_panel(1, web_server.server.state)
                    Panels.representation_panel(web_server.vtk_files_dict)


    

    

        
