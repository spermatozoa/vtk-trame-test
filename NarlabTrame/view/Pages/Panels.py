from trame.widgets import vuetify
from NarlabTrame.controller.Constant import Representation, ColorLookupTable
from NarlabTrame.model import VtkFile

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

def warp_panel(defalut_scale_factor, reset_scale_factor):
    """

    Args:
        defalut_scale_factor (float or int): UI default scale factor
        reset_scale_factor (function): callback to reset state.reset_scale_factor
    """
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
                v_model=("scale_factor", defalut_scale_factor),
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
                v_model=("scale_factor", defalut_scale_factor),
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

def representation_panel(vtk_files_list: list):
    """

    Args:
        vtk_files_list (list): list of VtkFile
    """
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
                for i in range(len(vtk_files_list)):
                    vuetify.VSelect(
                        # Color By
                        v_show=(f"{i}==cur_vtk_id"),
                        label="Color by",
                        v_model=("color_array_idx", 0),
                        items=(f"array_list{i}", 
                            [{"text": s, "value": i} for i, s in enumerate(vtk_files_list[i].scalar_list)],
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