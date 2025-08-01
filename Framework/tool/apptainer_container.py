import os
import subprocess
import shutil
from logger import logger
from .container_base import ContainerBase

class ApptainerContainer(ContainerBase):
    """
    Apptainer container implementation
    """
    
    def __init__(self, repository_name, tag_name, container_name, localhost_dir, container_dir, gpu=False):
        super().__init__(repository_name, tag_name, container_name, localhost_dir, container_dir, gpu)
        
        # For Apptainer, we expect .sif files instead of Docker images
        # Convert docker image name to .sif file path
        self.sif_file = self._get_sif_file_path()
        
        # Ensure the SIF file exists
        if not os.path.exists(self.sif_file):
            raise FileNotFoundError(f"Apptainer SIF file not found: {self.sif_file}")
            
        logger.info(f"Using Apptainer SIF file: {self.sif_file}")
        
    def _get_sif_file_path(self):
        """
        Convert Docker image reference to SIF file path
        Expected format: /path/to/sif/files/{repository_name}_{tag_name}.sif
        """
        # Get the directory containing the vul4c.py script (Framework directory)
        framework_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Go up one level to the project root
        project_root = os.path.dirname(framework_dir)
        
        # SIF directory
        sif_dir = os.path.join(project_root, "sif_images")
        
        # Convert repository name to filename-safe format
        safe_repo_name = self.repository_name.replace("/", "_")
        sif_filename = f"{safe_repo_name}_{self.tag_name}.sif"
        
        return os.path.join(sif_dir, sif_filename)
    
    def exec_command(self, command: str, workdir="/", env=dict(), user="root"):
        """
        Execute a command in the Apptainer container
        """
        try:
            # Build the apptainer exec command
            apptainer_cmd = ["module", "load", "apptainer", "&&", "apptainer", "exec"]
            
            # Disable automatic home directory mounting to avoid path conflicts
            apptainer_cmd.append("--no-home")
            
            # Add GPU support if needed
            if self.gpu:
                apptainer_cmd.append("--nv")
            
            # Add bind mounts
            apptainer_cmd.extend(["--bind", f"{self.localhost_dir}:{self.container_dir}"])
            
            # Add working directory
            if workdir != "/":
                apptainer_cmd.extend(["--pwd", workdir])
            
            # Add the SIF file
            apptainer_cmd.append(self.sif_file)
            
            # Add the command directly without wrapping in bash -c
            # Let the calling code decide if it needs bash -c
            if command.startswith("bash -c"):
                # If command already starts with bash -c, use it as is
                apptainer_cmd.append(command)
            else:
                # For simple commands, wrap in bash -c
                apptainer_cmd.extend(["bash", "-c", command])
            
            # Convert to shell command string to handle module load
            shell_cmd = " ".join(apptainer_cmd)
            
            # Set up environment
            exec_env = os.environ.copy()
            exec_env.update(env)
            
            logger.info(f"[APPTAINER_CMD] {shell_cmd}")
            logger.info(f"Working directory: {self.localhost_dir}")
            logger.info(f"Bind mount: {self.localhost_dir} -> {self.container_dir}")
            
            # Execute the command using shell
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=exec_env,
                cwd=self.localhost_dir
            )
            
            exit_code = result.returncode
            output = result.stdout
            
            # Log output for debugging
            if output:
                logger.info("=== CONTAINER OUTPUT ===")
                for line in output.split("\n"):
                    if line.strip():
                        logger.info(f"STDOUT: {line}")
                logger.info("=== END CONTAINER OUTPUT ===")
            
            # Log errors if any
            if result.stderr:
                logger.warning("=== CONTAINER STDERR ===")
                for line in result.stderr.split("\n"):
                    if line.strip():
                        logger.warning(f"STDERR: {line}")
                logger.warning("=== END CONTAINER STDERR ===")
            
            # Log exit code
            logger.info(f"Container command exit code: {exit_code}")
            
            return exit_code, output
            
        except Exception as ex:
            logger.error(f"Error executing Apptainer command: {ex}")
            raise ex
    
    def file_exists(self, file_path):
        """Check if a file exists in the container"""
        exist_command = f'"test -f {file_path}"'
        exit_code, _ = self.exec_command(exist_command)
        return exit_code == 0
    
    def dir_exists(self, dir_path):
        """Check if a directory exists in the container"""
        exist_command = f'"test -d {dir_path}"'
        exit_code, _ = self.exec_command(exist_command)
        return exit_code == 0
    
    def find_file(self, dir_path, maxdepth, name):
        """Find files matching a pattern"""
        # Use the exact same find command that works manually
        find_command = f'"find {dir_path} -maxdepth {maxdepth} -name {name}"'
        exit_code, output = self.exec_command(find_command)
        
        if exit_code == 0 and output.strip():
            # Extract just the filename from the full path
            files = []
            for line in output.split("\n"):
                if line.strip():
                    filename = os.path.basename(line.strip())
                    if filename:
                        files.append(filename)
            return files
        return []
    
    def cp_file(self, from_path, to_path):
        """Copy files within the container"""
        cp_command = f'"cp -r {from_path} {to_path}"'
        exit_code, _ = self.exec_command(cp_command)
        return exit_code == 0
    
    def add_permissions(self, file_path):
        """Add permissions to a file/directory"""
        permission_command = f'"chmod -R a+x {file_path}"'
        exit_code, _ = self.exec_command(permission_command)
        return exit_code == 0
    
    def cleanup(self):
        """Clean up container resources (no-op for Apptainer)"""
        logger.info(f"Cleaning up Apptainer container: {self.container_name}")
        # Apptainer doesn't require explicit cleanup like Docker containers
        pass
    
    # Additional properties for compatibility with existing code
    @property
    def container(self):
        """Fake container object for compatibility"""
        return type('obj', (object,), {'id': self.container_name})
    
    @property
    def id(self):
        """Container ID for compatibility"""
        return self.container_name
