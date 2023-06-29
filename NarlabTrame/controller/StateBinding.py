from NarlabTrame.controller.Constant import *
from NarlabTrame.controller.WebServer import *
    

cur_dir_idx  = 0
cur_vtk_file_idx = 0

def getVtkFile(sub_dir_idx=-1, vtk_file_idx=-1) -> VtkFile:
    """

    Args:
        sub_dir_idx (int, optional): pass -1 to get cur_ctk_file. Defaults to -1.
        vtk_file_idx (int, optional): pass -1 to get cur_ctk_file. Defaults to -1.

    Returns:
        _type_: VtkFile
    """
    global cur_dir_idx
    global cur_vtk_file_idx
    if sub_dir_idx == -1:
        # print(cur_dir_idx)
        # print(cur_vtk_file_idx)
        return vtk_files_dict[sub_dir_list[cur_dir_idx]][cur_vtk_file_idx]
    return vtk_files_dict[sub_dir_list[sub_dir_idx]][vtk_file_idx]
# bind state
state.sub_dir_list = sub_dir_list
state.cur_dir_idx = cur_dir_idx
state.cur_vtk_file_id = 0


@state.change("cube_axes_visibility")
def update_cube_axes_visibility(cube_axes_visibility, **kwargs):
    # cube_axes.SetVisibility(cube_axes_visibility)
    ctrl.view_update()

@state.change("warp_vector_idx")
def update_warp_vector(warp_vector_idx, **kwargs):
    cur_vtk = getVtkFile()
    cur_vtk.state_cache["warp_vector_idx"] = warp_vector_idx
    cur_vtk.reader.SetVectorsName(cur_vtk.vector_list[warp_vector_idx])
    ctrl.view_update()

@state.change("scale_factor")
def update_scale_factor(scale_factor, **kwargs):
    cur_vtk = getVtkFile()
    cur_vtk.state_cache["scale_factor"] = scale_factor
    cur_vtk.warp_vector.SetScaleFactor(scale_factor)
    # print("set scale factor: ", scale_factor)
    ctrl.view_update()

def reset_scale_factor(self):
    state.scale_factor = 1

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
    cur_vtk = getVtkFile()
    cur_vtk.state_cache["representation_mode"] = representation_mode
    property = cur_vtk.actor.GetProperty()
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
    else:
        return
    ctrl.view_update()

@state.change("color_map")
def update_colormap(color_map, **kwargs):    
    cur_vtk = getVtkFile()
    cur_vtk.state_cache["color_map"] = color_map
    lut = cur_vtk.actor.GetMapper().GetLookupTable()
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
    else:
        return
    lut.Build()
    ctrl.view_update()

@state.change("color_array_idx")
def update_color_by_name(color_array_idx, **kwargs):
    cur_vtk = getVtkFile()
    cur_vtk.state_cache["color_array_idx"] = color_array_idx
    scalar_list = cur_vtk.scalar_list
    reader = cur_vtk.reader
    if len(scalar_list) > 0: # in case some file do not have scalar
        vtk_pipeline.vtk_window.scalar_bar.SetTitle(scalar_list[color_array_idx])
        reader.SetScalarsName(scalar_list[color_array_idx])
        reader.Update()  # Needed because of GetScalarRange
        scalar_range = reader.GetOutput().GetScalarRange()    
        mapper = cur_vtk.actor.GetMapper()    
        # mapper.SetScalarRange(scalar_range)  not work
        mapper.GetLookupTable().SetRange(scalar_range)
        mapper.SetScalarVisibility(True)
        mapper.SetUseLookupTableScalarRange(True)
        ctrl.view_update()

@state.change("sub_dir_index","file_index")
def update_sub_dir_index(sub_dir_index, file_index, **kwargs):
    # check if variable exist (getserver() before create global variable)
    global cur_dir_idx
    global cur_vtk_file_idx    
    def change_actor():
        old_vtk = getVtkFile()
        new_vtk = getVtkFile(sub_dir_index, file_index)
        old_vtk.setVisibility(False)           
        new_vtk.setVisibility(True)
        
        scalar_bar = vtk_pipeline.vtk_window.scalar_bar
        if new_vtk.scalar_list == []:
            scalar_bar.SetVisibility(0)
        else:
            lut = new_vtk.actor.GetMapper().GetLookupTable()
            scalar_bar.SetLookupTable(lut)
            scalar_bar.SetTitle(new_vtk.scalar_list[0])
            scalar_bar.SetVisibility(1)
        state.cur_vtk_file_id = new_vtk.id                  
        
        
    try:
        if cur_dir_idx == sub_dir_index:
            if cur_vtk_file_idx == file_index:
                return
            else:
                change_actor()
                cur_vtk_file_idx = file_index
        else:
            if file_index != 0:       # to avoid changing dir cause vtk_file_index out of range, we need to read index [0] VtkFile
                state.file_index = 0  # this will triger update_sub_dir_index() again, so we can simply return after change state.file_index
                return
            change_actor()
            cur_dir_idx = sub_dir_index
            cur_vtk_file_idx = file_index
            state.cur_dir_idx = sub_dir_index
        state.update(getVtkFile().state_cache)
        ctrl.view_update()
        
    except NameError as e: 
        print(e)
        print("NameError: maybe some variable need to be global variable")
        return