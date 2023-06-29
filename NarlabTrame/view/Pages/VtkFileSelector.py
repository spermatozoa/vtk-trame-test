from trame.widgets import vuetify

def vtk_file_chooser(sub_dir_list:list, sub_dir_files:dict):
    """UI for selecting different files in each sub dir

    Args:
        sub_dir_list (list): list of sub dir names
        sub_dir_files (dict): dict of VtkFiles
        
    """
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

    # create file names VSelect for each sub dir, using v-if to control which is enable
    for i in range(len(sub_dir_list)):   
        # print(sub_dir_files[sub_dir_list[i]])         
        s = vuetify.VSelect(
            # FileSelect
            v_if=(f"{i}==sub_dir_index",),
            v_model=("file_index", 0),
            items=(
                f"files{i}",
                [{"text": vtkfile.file_name, "value": idx} for idx, vtkfile in enumerate(sub_dir_files[sub_dir_list[i]])],
            ),
            label="vtkFile",
            # value=vector_list[0],
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
