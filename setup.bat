@echo off
echo Starting infrastructure setup...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Initialize Terraform
echo Initializing Terraform...
terraform init

REM Apply Terraform configuration
echo Applying Terraform configuration...
terraform apply -auto-approve

REM Run Python setup script
echo Running Python setup script...
python setup.py

echo Setup complete!
pause
