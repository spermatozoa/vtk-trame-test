import os
import argparse

class WebServer():
    
    def __init__(self):
        """ Initialize class
        
        Returns: 
            None
        """
        self.base_dir = self.parseArgument().dir
        self.sub_dir_list, self.sub_files_dict = self.getSubDirFile(self.base_dir)
        self.cur_sub_dir_idx = 0
        self.cur_file_idx = 0

    def parseArgument(self):
        """Parse command line argument

        Returns:
            dict: arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--base-dir", help="Directory to vtk files (abs path)", dest="dir", required=True)
        return parser.parse_args()
    
    def getSubDirFile(root_dir):
        """_summary_

        Args:
            root_dir (str): abs path of base dir

        Raises:
            Exception: description of error

        Returns:
            list: sub dir name in list
            dict: key = sub dir name, value = list of files name in sub dir
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
                        file_list.append(f)
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
    
    def getVtkFileName(sub_dir_idx=0, file_idx=0, id=-1):
        if id != -1:
            for key, val in vtk_file_dict.items():
                if val['id'] == id:
                    return key
            return sub_dir_files[sub_dir_list[sub_dir_idx]][file_idx]
    def getVtkFilePath(sub_dir_idx, file_idx):
        return os.path.join(root_dir, sub_dir_list[sub_dir_idx], getVtkFileName(sub_dir_idx, file_idx))
    

