from NarlabTrame.model.VtkWindow import VtkWindow

class VtkPipeline():
    def __init__(self, vtk_files_dict) :     
        """Setup vtkwindow
        """   
        self.vtk_window = self.setVtkWindow(vtk_files_dict)
    
        
    def setVtkWindow(self, vtk_files_dict:dict) -> VtkWindow:
        """

        Args:
            vtk_files_dict (dict): dict contains all VtkFile \n
            ex: {"sub_dir_name": VtkFile}

        Returns:
            VtkWindow
        """
        vtk_window = VtkWindow()
        # let vtkfile display in renderer
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