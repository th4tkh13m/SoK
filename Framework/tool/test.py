from tool.container_factory import ContainerClass
from tool.data import Data
from logger import logger
import os
import sys

class Test(ContainerClass):

    config_file=""
    result_dir="/vul4c_result"

    def __init__(
            self,
            localhost_dir, 
            container_dir,
            work_dir,
            container_name,
            data=Data,
            repository_name="vul4c/test",
            tag_name="1.0",  
            gpu=False
    ):
        super().__init__(repository_name, tag_name, container_name, localhost_dir, container_dir, gpu)
        self.work_dir=work_dir
        self.data = data

    def config(self):
        config_file=os.path.join(self.work_dir,"config")
        setup_file=os.path.join(self.work_dir,"setup.sh")
        test_file=os.path.join(self.work_dir,"test.sh")

        test_exist=self.file_exists(test_file)
        if not test_exist:
            logger.warning(f"this data dont have test")
            raise RuntimeError(f"this data dont have test")

        alternate_path_command=f"bash -c \"sed -i 's#<path>#{self.work_dir}#g' {config_file}\""
        self.exec_command(alternate_path_command)
        logger.info(f"alternate the path in config with command {alternate_path_command}")
        
        setup_command=f"bash -c \"rm -rf source && bash {setup_file}\""
        exit_code,output=self.exec_command(setup_command,workdir=self.work_dir)
        if exit_code != 0:
            logger.error(f"An error occurred when the project was built through setup with an error code {exit_code}")
            raise RuntimeError(f"An error occurred when the project was built through setup with an error code {exit_code}")
        
        self.config_file=config_file
        self.test_file=test_file

    #fix-file-path save the relative path of fix file and split with "|"
    def parse_config_file(self, config_file):
        with open(config_file, mode="r") as f:
            contents=f.read().split("\n")
        dic={}
        for content in contents:
            if content!="":
                l=content.split("=")
                dic[l[0]]=l[1].strip()
        self.data.fix_file=dic['fix-file-path']
        

    def test(self):
        test_result=dict()
        for dir in os.listdir(self.data.runtime_host):
            candidate_dir=os.path.join(self.data.runtime_host,dir)
            if not os.path.isdir(candidate_dir):
                # candidate_list.append(candidate_dir)
                continue
            config_file=os.path.join(candidate_dir,"config")
            if os.path.exists(os.path.join(candidate_dir,"config")):
                self.parse_config_file(config_file)
            
            files=[os.path.split(item)[1] for item in self.data.fix_file.split("|")]
            if len(files)==1:
                old_file=files[0]
                if os.path.exists(os.path.join(candidate_dir,old_file)):
                    new_files=[os.path.join(candidate_dir,old_file)]
                elif os.path.exists(os.path.join(candidate_dir,"file.new.c")):
                    new_files=[os.path.join(candidate_dir,"file.new.c")]
                elif os.path.exists(os.path.join(candidate_dir,"patch_file")):
                    new_files=[os.path.join(candidate_dir,"patch_file")]
            else:
                new_files=[os.path.join(candidate_dir,item) for item in files]
            
            #replace the abs path in host with th abs path in container
            new_files=[self.data.host_path_2_container_path(item) for item in new_files] 

            new_files="|".join(new_files)
            
            test_command=f"bash -c \"bash {self.test_file} {self.data.source} {new_files} {self.data.fix_file}\""
            exit_code,output=self.exec_command(test_command,workdir=self.work_dir)
        
            if exit_code != 0:
                test_result[dir]=False
            else:
                test_result[dir]=True
        return test_result

    def save_result(self,test_result_dic):

        contents=""
        for key,value in test_result_dic.items():
            if value:
                contents+=f"{key}:Pass\n"
            else:
                contents+=f"{key}:Fail\n"
        test_result_file=os.path.join(self.data.abs_path_host,"test_result")

        with open(test_result_file, mode='w') as f:
            f.write(contents)

        mkdir_command=f"bash -c \"mkdir {self.result_dir}\""
        exit_code,output=self.exec_command(mkdir_command)

        self.cp_file(test_result_file,self.result_dir)

    def run(self):
        self.config()
        test_result=self.test()
        self.save_result(test_result)
    
                