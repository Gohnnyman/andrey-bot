# HOW TO
```bash
# Install dependencies
pip install playwright --user 
playwright install



# Make UNIX binary
python -m PyInstaller --onefile --add-data ~/.cache/ms-playwright:playwright/driver/package/.local-browsers main.py

```