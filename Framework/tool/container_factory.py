import os
from logger import logger

# Configuration for container backend
CONTAINER_BACKEND = os.environ.get("VUL4C_CONTAINER_BACKEND", "apptainer").lower()

def get_container_class():
    """
    Factory function to get the appropriate container class based on configuration
    """
    if CONTAINER_BACKEND == "docker":
        try:
            from .container import DockerContainer
            logger.info("Using Docker container backend")
            return DockerContainer
        except ImportError as e:
            logger.error(f"Docker backend requested but Docker SDK not available: {e}")
            logger.info("Falling back to Apptainer backend")
            from .apptainer_container import ApptainerContainer
            return ApptainerContainer
    elif CONTAINER_BACKEND == "apptainer":
        from .apptainer_container import ApptainerContainer
        logger.info("Using Apptainer container backend")
        return ApptainerContainer
    else:
        raise ValueError(f"Unsupported container backend: {CONTAINER_BACKEND}. Use 'docker' or 'apptainer'")

# For backward compatibility, create an alias
ContainerClass = get_container_class()
