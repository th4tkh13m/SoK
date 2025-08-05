import os
import subprocess

def execute_command(command: str, show_output=True, env=dict(), dir=None):
    if not dir:
        dir = os.getcwd()
    print(f"[{dir}] {command}")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env, cwd=dir)

    try:
        output, error = proc.communicate(timeout=3600)  # Set a timeout of 1 hour
    except subprocess.TimeoutExpired:
        proc.kill()
        output, error = proc.communicate()
        print("Command timed out, output:")
        print(output.decode())
        print(error.decode())

    return int(proc.returncode), output.decode(), error.decode()

def main():
    framework_dir = os.path.join(os.getcwd(), "Framework")
    tools = [d for d in os.listdir(framework_dir) if os.path.isdir(os.path.join(framework_dir, d)) and d != 'tool' and d != '__pycache__']

    for tool in tools:
        tool_dir = os.path.join(framework_dir, tool)
        softwares = [s for s in os.listdir(tool_dir) if os.path.isdir(os.path.join(tool_dir, s)) and s != 'INSTRUMENT']

        for software in softwares:
            software_dir = os.path.join(tool_dir, software)
            cves = [c for c in os.listdir(software_dir) if os.path.isdir(os.path.join(software_dir, c))]

            for cve in cves:
                command = f"/data/khiem/miniconda3/envs/oppyai/bin/python {os.path.join(framework_dir, 'vul4c.py')} --tool \"{tool}\" --software \"{software}\" --CVEID \"{cve}\""
                return_code, stdout, stderr = execute_command(command)
                if return_code != 0:
                    print(f"Error executing command: {command}")
                    print(f"stdout: {stdout}")
                    print(f"stderr: {stderr}")

if __name__ == "__main__":
    main()