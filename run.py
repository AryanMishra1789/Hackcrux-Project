import os
import sys
import subprocess
import shutil

def find_python():
    """Find Python 3.11 executable in the system."""
    # Common Python installation paths on Windows
    possible_paths = [
        r"C:\Python311\python.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe",
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files (x86)\Python311\python.exe"
    ]
    
    # Check if python3.11 is in PATH
    python_311 = shutil.which('python3.11')
    if python_311:
        return python_311
    
    # Check possible installation paths
    for path in possible_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            return expanded_path
    
    return None

def run_app():
    # First try to find Python 3.11
    python_path = find_python()
    
    if not python_path:
        print("Error: Python 3.11 not found. Please install Python 3.11 from:")
        print("https://www.python.org/downloads/release/python-3116/")
        print("\nMake sure to check 'Add Python to PATH' during installation.")
        return

    print(f"Using Python at: {python_path}")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        try:
            subprocess.run([python_path, '-m', 'venv', 'venv'], check=True)
            print("Virtual environment created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return

    # Get the virtual environment Python path
    if sys.platform == 'win32':
        venv_python = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join('venv', 'bin', 'python')

    if not os.path.exists(venv_python):
        print("Error: Virtual environment Python not found!")
        return

    # Install requirements if needed
    if not os.path.exists(os.path.join('venv', 'Lib', 'site-packages', 'fastapi')):
        print("Installing requirements...")
        try:
            subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return

    # Run the FastAPI app
    print("Starting FastAPI application...")
    try:
        subprocess.run([venv_python, 'app.py'])
    except Exception as e:
        print(f"Error running app.py: {e}")

if __name__ == "__main__":
    run_app() 