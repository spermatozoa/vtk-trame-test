import os
from trame.app import get_server
from NarlabTrame.model import VtkPipeline, VtkFile
from NarlabTrame.view.IndexPage import IndexPage
from NarlabTrame.controller.StateBinding import StateBinding

class WebServer():    
    def __init__(self):
        """ Initialize trame server and vtk pipeline
        
        Returns: 
            None
        """
        self.server = get_server()
        self.base_dir = self.parseArgument(self.server).dir
        self.sub_dir_list, self.vtk_files_dict = self.getSubDirVtkFile(self.base_dir)
        self.cur_sub_dir_idx = 0
        self.cur_vtk_file_idx = 0
        self.vtk_pipeline = VtkPipeline.VtkPipeline(self.vtk_files_dict)
        self.index_page = IndexPage(self, self.vtk_pipeline.vtk_window.render_window, self.vtk_pipeline.vtk_window.orientation_marker_widget)
        self.state_bind = StateBinding(self.server, self)
        

    def parseArgument(self, trame_server):
        """Parse command line argument

        Returns:
            dict: arguments
        """
        trame_server.cli.add_argument("-b", "--base-dir", help="Directory to vtk files (absolute path)", dest="dir", required=True)
        args = trame_server.cli.parse_args()
        return args
    
    def getSubDirVtkFile(self, root_dir):
        """ parse file in dir and construct to class 'VtkFile'
        
        Args:
            root_dir (str): abs path of base dir

        Raises:
            Exception: description of error

        Returns:
            list: sub dir name in list
            dict: key = sub dir name, value = list of VtkFile()
        """
        if not root_dir:
            raise Exception("Base dir should not be empty")
        sub_dir_files = {}
        sub_dir_list = []
        for item in os.listdir(root_dir):
            sub_path = os.path.join(root_dir, item)
            if os.path.isdir(sub_path):
                sub_dir_list.append(item)
                file_list = []
                for f in os.listdir(sub_path):
                    f_path = os.path.join(sub_path, f)
                    if os.path.isfile(f_path):
                        v = VtkFile.VtkFile(f, f_path)
                        file_list.append(v)
                    elif os.path.isdir(f_path):
                        print("there is dir in ", sub_path)
                sub_dir_files[item] = file_list
            elif os.path.isfile(sub_path):
                print("there is file in ", root_dir)        
        if not sub_dir_list:
            raise Exception("no sub dir")
        elif not sub_dir_files:
            raise Exception("no file in sub dir")
        return sub_dir_list, sub_dir_files
    
    def getVtkFile(self, sub_dir_idx=-1, vtk_file_idx=-1) -> VtkFile:
        """

        Args:
            sub_dir_idx (int, optional): pass -1 to get cur_ctk_file. Defaults to -1.
            vtk_file_idx (int, optional): pass -1 to get cur_ctk_file. Defaults to -1.

        Returns:
            _type_: VtkFile
        """
        if sub_dir_idx == -1:
            return self.vtk_files_dict[self.sub_dir_list[self.cur_sub_dir_idx]][self.cur_vtk_file_idx]
        return self.vtk_files_dict[self.sub_dir_list[sub_dir_idx]][vtk_file_idx]
    
    def start(self):
        """start trame server
        """
        self.server.start()
        

