from tool.container_factory import ContainerClass
from logger import logger
import os
import sys

class VQM(ContainerClass):

    def __init__(
            self,
            localhost_dir, 
            container_dir,
            work_dir,
            container_name,
            new_file_name,
            old_file_name,
            cwe_id,
            cve_id,
            repository_name="vul4c/vqm",
            tag_name="1.0",  
            gpu=True
    ):
        super().__init__(repository_name, tag_name, container_name, localhost_dir, container_dir, gpu)
        self.work_dir=work_dir
        self.new_file_name=new_file_name
        self.old_file_name=old_file_name
        self.cwe_id=cwe_id
        self.cve_id=cve_id
        self.result_dir="/vul4c_result"
    

    def preprocess(self):
        preprocess_command=f"bash -c \"source /root/env_VRepair.sh && python3 preprocess.py  {self.old_file_name} {self.new_file_name} {self.cwe_id} {self.cve_id}\""
        exit_code,output=self.exec_command(preprocess_command,workdir=self.work_dir)
        if exit_code != 0:
            logger.error(f"An error occurred when the project was preprocessed VRepair")
            raise RuntimeError(f"An error occurred when the project was preprocessed VRepair")

        
    def inference(self):
        inference_command=f"bash -c \"source /root/env_VQM.sh && python run_generate_changed.py \
        --num_beams 50 \
        --model_name=vqr_fine_tuned_model.bin \
        --output_dir=./saved_models \
        --tokenizer_name=Salesforce/codet5-base \
        --model_name_or_path=Salesforce/codet5-base \
        --do_test \
        --test_data_file=/{self.work_dir}/{self.cve_id}.csv \
        --generated_output_dir=/{self.work_dir} \
        --encoder_block_size 512 \
        --vul_repair_block_size 256 \
        --eval_batch_size 1 \
        --seed 123456  2>&1 | tee temp.log\""

        exit_code,output=self.exec_command(inference_command,workdir="/exp/VQM.new/VQM")

        if exit_code != 0:
            logger.error(f"An error occurred while inference with VulMaster")
            raise RuntimeError(f"An error occurred while inference with VulMaster")
        else:
            logger.info("inference ended successfully")
    
    def restore(self):
        restore_command =f"bash -c \"source /root/env_VRepair.sh && python3 restore.py\""
        exit_code,output=self.exec_command(restore_command,workdir=self.work_dir)
        
        if exit_code != 0:
            logger.error(f"An error occurred while resotre with VRepair")
            raise RuntimeError(f"An error occurred while restore with VRepair")
        else:
            logger.info("restore ended successfully")
    
    def run(self):
        self.preprocess()
        self.inference()
        self.restore()
                