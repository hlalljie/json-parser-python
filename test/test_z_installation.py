import subprocess
import sys
import venv
import os
import shutil

def test_installation() -> None:
    """Test that the CLI can be installed in a virtual environment
    
    This test is intended to be run with pytest.
    """

    # Save the current working directory
    original_cwd = os.getcwd()

    try:
        # Change to the project root or wherever necessary
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
        os.chdir(project_root)

        # Create a temporary virtual environment
        venv_dir = os.path.join(script_dir, 'temp_venv')
        python_executable = os.path.join(venv_dir, 'bin', 'python')

        # Create the virtual environment
        print(f"Creating virtual environment at {venv_dir} using {sys.executable}")
        venv.create(venv_dir, with_pip=True, clear=True, symlinks=True, system_site_packages=False)

        # Check that the Python executable exists
        if not os.path.exists(python_executable):
            raise FileNotFoundError("Virtual environment's Python executable" \
                f"not found at {python_executable}")

        # Install the CLI
        print(f"Installing CLI in the virtual environment using {python_executable}")
        subprocess.run([python_executable, '-m', 'pip', 'install', '.'], check=True)

        # Run the CLI command as a test
        cli_executable = os.path.join(venv_dir, 'bin', 'validate_json')
        json_file_path = os.path.join(project_root, 'test', 'test_data', 'file', 'valid.json')
        result = subprocess.run(['validate_json', json_file_path], capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # Check the return code and validate the output
        assert result.returncode == 0, f"CLI command failed with return code {result.returncode}"
        assert "JSON is valid" in result.stdout  # Replace with actual expected output

    finally:
        # Change back to the original working directory
        os.chdir(original_cwd)

        # Clean up: remove the temporary virtual environment
        if os.path.exists(venv_dir):
            shutil.rmtree(venv_dir)
        else:
            print(f"Warning: {venv_dir} directory not found during cleanup.")
