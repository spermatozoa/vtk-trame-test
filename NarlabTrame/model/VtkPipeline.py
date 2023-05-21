import VtkFile, VtkWindow

class VtkPipeline():
    def __init__(self, vtk_files_dict) :        
        self.vtk_window = self.setVtkWindow(vtk_files_dict)
    
        
    def setVtkWindow(self, vtk_files_dict):
        vtk_window = VtkWindow()
        # let vtkfile display in renderer)
        first_vtk = None
        for k in vtk_files_dict.keys():
            for vf in vtk_files_dict[k]:
                if not first_vtk:
                    first_vtk = vf
                vtk_window.addActor(vf.actor)
        vtk_window.updateScalarBar(first_vtk)
        first_vtk.setVisibility(True)
        vtk_window.resetCamera()
        
        return vtk_window