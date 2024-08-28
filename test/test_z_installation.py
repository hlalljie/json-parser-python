import subprocess
import sys
import venv
import os
import shutil
import pytest

def test_cli_installation():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    venv_dir = os.path.join(script_dir, 'temp_venv')
    python_executable = os.path.join(venv_dir, 'bin', 'python')

    try:
        print(f"Creating virtual environment at {venv_dir} using {sys.executable}")
        venv.create(venv_dir, with_pip=True, clear=True, symlinks=True, system_site_packages=False)

        if not os.path.exists(python_executable):
            raise FileNotFoundError(f"Virtual environment's Python executable not found at {python_executable}")

        os.chdir(project_root)

        print(f"Installing CLI in the virtual environment using {python_executable}")
        subprocess.run([python_executable, '-m', 'pip', 'install', '.'], check=True)

        # Debug: Show installed files
        installed_files = subprocess.run([python_executable, '-m', 'pip', 'show', '-f', 'validate_json'], capture_output=True, text=True)
        print("Installed files:", installed_files.stdout)

        cli_executable = os.path.join(venv_dir, 'bin', 'validate_json')
        json_file_path = os.path.join(project_root, 'test', 'test_data', 'file', 'valid.json')
        print(f"Running CLI command: {cli_executable} {json_file_path}")

        # Pass the file as an argument to the CLI command
        result = subprocess.run([cli_executable, json_file_path], capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # Check the return code and validate the output (modify as per your expected output)
        assert result.returncode == 0, f"CLI command failed with return code {result.returncode}"
        assert "JSON is valid" in result.stdout  # Replace with actual expected output

    finally:
        os.chdir(script_dir)
        if os.path.exists(venv_dir):
            shutil.rmtree(venv_dir)
        else:
            print(f"Warning: {venv_dir} directory not found during cleanup.")

if __name__ == "__main__":
    test_cli_installation()
