import subprocess
import os

def run_tests():
    # Run pytest
    result = subprocess.run(['pytest'], capture_output=True)
    return result.returncode == 0

def mount_python_to_docker(image_name, python_file_path, docker_mount_path):
    # Check if the Python file exists
    if not os.path.exists(python_file_path):
        print("Python file does not exist.")
        return
    if run_tests():
         print("Tests are successful, now running containers...")
         # Run the Docker container with the mounted Python file
         #subprocess.run(['docker', 'run', '-v', f"{python_file_path}:{docker_mount_path}", image_name])
         subprocess.run(['docker-compose', 'up', '-d'])
    else:
         print("Tests failed, aborting...")

if __name__ == "__main__":
    image_name ="appbkend"
    python_file_path = "./"
    docker_mount_path = "/app/"

    mount_python_to_docker(image_name, python_file_path, docker_mount_path)
