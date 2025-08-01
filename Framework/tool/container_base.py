import os
import subprocess
from abc import ABC, abstractmethod
from logger import logger

class ContainerBase(ABC):
    """
    Abstract base class for container implementations (Docker, Apptainer, etc.)
    """
    
    def __init__(self, repository_name, tag_name, container_name, localhost_dir, container_dir, gpu=False):
        self.repository_name = repository_name
        self.tag_name = tag_name
        self.container_name = container_name
        self.localhost_dir = localhost_dir
        self.container_dir = container_dir
        self.gpu = gpu
        
        # Derived attributes
        self.image_name = f"{self.repository_name}:{self.tag_name}"
        
    @abstractmethod
    def exec_command(self, command: str, workdir="/", env=dict(), user="root"):
        """
        Execute a command in the container
        Returns: (exit_code, output)
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path):
        """Check if a file exists in the container"""
        pass
    
    @abstractmethod
    def dir_exists(self, dir_path):
        """Check if a directory exists in the container"""
        pass
    
    @abstractmethod
    def find_file(self, dir_path, maxdepth, name):
        """Find files matching a pattern"""
        pass
    
    @abstractmethod
    def cp_file(self, from_path, to_path):
        """Copy files within the container"""
        pass
    
    @abstractmethod
    def add_permissions(self, file_path):
        """Add permissions to a file/directory"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up container resources"""
        pass
