import os
from trame.app import get_server
from NarlabTrame.model import VtkPipeline, VtkFile
from NarlabTrame.view.IndexPage import IndexPage

def parseArgument(trame_server):
    """Parse command line argument

    Returns:
        dict: arguments
    """
    trame_server.cli.add_argument("-b", "--base-dir", help="Directory to vtk files (absolute path)", dest="dir", required=True)
    args = trame_server.cli.parse_args()
    return args
    
def getSubDirVtkFile(root_dir):
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

def start():
    """start trame server
    """
    server.start()
    

# init server
server = get_server()
state = server.state
ctrl = server.controller

# parse args and load VtkFile
base_dir = parseArgument(server).dir
sub_dir_list, vtk_files_dict = getSubDirVtkFile(base_dir)

vtk_pipeline = VtkPipeline.VtkPipeline(vtk_files_dict)
index_page = IndexPage(vtk_pipeline.vtk_window.render_window, vtk_pipeline.vtk_window.orientation_marker_widget, server, sub_dir_list, vtk_files_dict)

import NarlabTrame.controller.StateBinding as sb
# 其實這一行就只是把StateBinding.py的東西直接搬過來而已，也就是把裡面的內容直接copy paste過來效果就跟這一行一樣
# 注意因為會用到server.state，所以get_server()一定要先跑


