# multiplex-heatmap
A small GUI utility to generate heat map plots from multiplex CSV data

## Installation

1. Open a Terminal 

1. Make a directory for your virtual environments (optional)
   
   ```
   cd
   mkdir envs
   ```

1. Change to the 'envs' directory and create a virtual environment using Python 3
   
   ```
   cd envs
   python3 -m venv py3-multiplex-heatmap
   ```   
  
1. Activate the new environment
   
   ```
   cd py3-multiplex-heatmap
   source bin/activate
   ```

1. Clone the multiplex-heatmap repository from Github (or download it and skip this step)
   
   ```
   git clone https://github.com/whitews/multiplex-heatmap
   ```

1. Install the Python packages required to run the app
   
   ```
   cd multiplex-heatmap
   pip install -r requirements.txt
   ```

## Running the Application

1. Open a Terminal

1. Change directories to the multiplex heatmap environment location

   ```
   cd
   cd envs/py3-multiplex-heatmap
   ```

1. Activate the environment

   ```
   source bin/activate
   ```
   
1. Change to the directory containing the app

   ```
   cd multiplex-heatmap
   ```

1. Run the application

   ```
   python multiplex_heatmap.py
   ```
