#!/bin/bash

# Compile script to compile svi with Nuitka

echo "Starting compilation of svi..."

# Set the PYTHONPATH to include system gi module and src directory
export PYTHONPATH=/usr/lib/python3/dist-packages:./src

# Configure ccache for faster recompilation
export CCACHE_SLOPPINESS=time_macros,include_file_mtime
export CCACHE_BASEDIR=$(pwd)
export CCACHE_NOHASHDIR=1

# Start the compilation
cd src
../venv/bin/python -m nuitka --standalone --onefile --include-data-file=ui.css=ui.css --follow-imports --include-module=completion_view --include-module=installation_view --include-module=partitioning_view --include-module=software_config_view --include-module=summary_view --include-module=welcome_view --include-module=system_config_view --include-module=user_config_view main.py

if [ $? -eq 0 ]; then
    # Move the generated binary to the parent directory
    mv main.bin ../svi
    echo "Compilation completed successfully!"
    echo "Binary \"svi\" has been created."
    ls -la ../svi
else
    echo "Compilation failed!"
    exit 1
fi
