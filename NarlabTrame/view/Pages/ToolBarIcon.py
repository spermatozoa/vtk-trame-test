from trame.widgets import vuetify

def tool_bar_icon():
    """set up toolbar icon at right up corner
    """
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