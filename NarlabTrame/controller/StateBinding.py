from NarlabTrame.controller.Constant import *
from NarlabTrame.controller.WebServer import *
    
def haha():
    print(state, "haha")
@state.change("cube_axes_visibility")
def update_cube_axes_visibility(cube_axes_visibility, **kwargs):
    # cube_axes.SetVisibility(cube_axes_visibility)
    ctrl.view_update()

@state.change("warp_vector_idx")
def update_warp_vector(warp_vector_idx, **kwargs):
    cur_vtk = getVtkFile()
    cur_vtk.reader.SetVectorsName(cur_vtk.vector_list[warp_vector_idx])
    ctrl.view_update()

@state.change("scale_factor")
def update_scale_factor(scale_factor, **kwargs):
    cur_vtk = getVtkFile()
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
    scalar_list = cur_vtk.scalar_list
    reader = cur_vtk.reader
    if len(scalar_list) > 0:
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
def update_sub_dir_index(sub_dir_index=cur_dir_idx, file_index=cur_vtk_file_idx, **kwargs):
    # check if variable exist (getserver() before create global variable will need to check this)
    global cur_dir_idx
    global cur_vtk_file_idx
    # print("sub_dir: ", sub_dir_index)
    # print("file: ", file_index)
    def change_actor():
        old_vtk = getVtkFile()
        new_vtk = getVtkFile(sub_dir_index, file_index)
        old_vtk.actor.SetVisibility(0)            
        new_vtk.actor.SetVisibility(1)
        
        scalar_bar = vtk_pipeline.vtk_window.scalar_bar
        if new_vtk.scalar_list == []:
            scalar_bar.SetVisibility(0)
        else:
            lut = new_vtk.actor.GetMapper().GetLookupTable()
            scalar_bar.SetLookupTable(lut)
            scalar_bar.SetTitle(new_vtk.scalar_list[0])
            scalar_bar.SetVisibility(1)
        
        #state.cur_vtk_id = new_vtk['id']
    # cur_sub_dir_idx = cur_sub_dir_idx
    # cur_file_idx = cur_vtk_file_idx
    try:
        if cur_dir_idx == sub_dir_index:
            if cur_vtk_file_idx == file_index:
                return
            else:
                change_actor()
                cur_vtk_file_idx = file_index
        else:
            change_actor()
            cur_dir_idx = sub_dir_index
            state.cur_sub_dir_idx = sub_dir_index
            cur_vtk_file_idx = 0
        
    except NameError:
        print("NameError")
        return
    # reader.SetFileName(getVtkFilePath(cur_sub_dir_idx, cur_file_idx))
    # reader.Update()
    # state.representation_mode = Representation.Surface.value
    # state.color_map = ColorLookupTable.Rainbow.value
    ctrl.view_update()