from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame, html
from ..controller.Constant import *
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
                    self.vtk_file_chooser()
                    self.warp_panel()
                    self.representation_panel()

    def tool_bar_icon(self):
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

    def drawer_panels(self, panel_header):
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

    def warp_panel(self):
        with self.drawer_panels(panel_header="WarpVector"):
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

        

