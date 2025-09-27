# Swiss {ai} Hackhathon 


### 1. Create a Virtual Environment
Run the following command to create a virtual environment:
```bash
python3 -m venv book_env
```

### 2. Activate the Virtual Environment
- On macOS/Linux:
  ```bash
  source book_env/bin/activate
  ```
- On Windows:
  ```bash
  book_env\Scripts\activate
  ```

### 3. Install Dependencies
Install the required libraries using UV:
```bash
uv sync --active
```
To add new dependencies, use:
```bash
uv add <package_name> --active
```
or manually edit the `pyproject.toml` file and then run:
```bash
uv sync --active
```
---

## Exemple: Running the Script

Once the environment is set up, run a script:
```bash
python -m streamlit run frontend/app.py
```

---

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```