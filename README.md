# HOW TO

## Running from source:

```bash
# Install dependencies
pip install playwright --user 
playwright install

# Make UNIX binary
python -m PyInstaller --onefile --add-data ~/.cache/ms-playwright:playwright/driver/package/.local-browsers main.py
```

## Running from binary:

Just download the binary and settings.json from the releases page and run it.