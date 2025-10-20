---
tags: [python, setup, checklist, development]
---
# The Ultimate Python Project Setup Checklist

A comprehensive guide for setting up new Python projects efficiently. Perfect for beginners learning Python project structure and experienced developers who want a streamlined setup process.

**Code Snippets:** All examples available on [GitHub Gist](https://gist.github.com/mikemurphyco)
**Python Project Setup Guide:** [GitHub Repository](https://github.com/mikemurphyco/python-project-setup-guide)

## 🚀 Quick Reference Checklist

### 📚 Traditional Workflow
- [ ] `mkdir my_project && cd my_project`
- [ ] `git init && echo ".venv/" >> .gitignore`
- [ ] `echo "3.11" > .python-version`
- [ ] `python3 -m venv .venv && source .venv/bin/activate`
- [ ] `touch requirements.txt requirements-dev.txt`
- [ ] `mkdir my_project tests && touch my_project/__init__.py tests/test_my_project.py`
- [ ] `touch README.md LICENSE .env.example`
- [ ] `pip install pytest black ruff pre-commit`
- [ ] `pip freeze > requirements-dev.txt`
- [ ] `mkdir sandbox && touch sandbox/.gitkeep`
- [ ] `git add . && git commit -m "Initial project setup"`
- [ ] `git remote add origin <repo-url> && git push -u origin main`

### 🚀 Modern Workflow (UV)
- [ ] `curl -LsSf https://astral.sh/uv/install.sh | sh` (one-time setup)
- [ ] `mkdir my_project && cd my_project`
- [ ] `uv init --python 3.11` (creates project structure + pyproject.toml)
- [ ] `uv add --dev pytest black ruff pre-commit` (much faster than pip)
- [ ] `git add . && git commit -m "Initial project setup"`
- [ ] `git remote add origin <repo-url> && git push -u origin main`

> **Note:** UV automatically creates `.gitignore`, `pyproject.toml`, `main.py`, `README.md`, and manages dependencies in lockfile format.

---

## 🛤️ Choose Your Workflow

Before diving into the detailed guide, choose the workflow that matches your situation:

### 📚 Traditional Workflow (Recommended for Learning)

**Use this if you are:**
- Learning Python fundamentals
- Following tutorials or courses
- Working in environments where pip is required
- Want maximum compatibility

**Tools:** `pip`, `python -m venv`, `requirements.txt`

### 🚀 Modern Workflow (Recommended for Production)

**Use this if you want:**
- 10-100x faster package installation
- All-in-one tool (replaces pip, pip-tools, virtualenv, etc.)
- Better dependency resolution and error messages
- Future-forward Python development

**Tools:** `uv` (replaces most traditional tools)

> **Note:** Both workflows achieve the same result. The modern workflow is simply faster and more efficient. You can switch between them anytime.

---

## 📚 Detailed Setup Guide

### 1. Create Project Folder

**Why:** This is the root directory of your project, keeping all files and folders organized in one place.

**Best Practices:**
- Use consistent naming: `my-awesome-project` or `my_project`
- Avoid spaces or special characters for compatibility with Git and tools

**Code Snippets (GitHub Gist):** [**01_create_project_folder**](https://gist.github.com/mikemurphyco/9faf634bfb2cac41e1858d4a08692987#file-01_create_project_folder)

```bash
# Create and navigate to project folder
mkdir my_project
cd my_project
```

### 2. Initialize Git and Create Essential Files

**Why:** 
- Git provides version control for tracking changes and collaboration
- `.gitignore` prevents unnecessary files from being committed
- `.gitattributes` ensures consistent line endings across platforms

**Best Practices:**
- Initialize Git immediately to track all project evolution
- Use comprehensive `.gitignore` templates for Python projects
- Set up line ending configuration for cross-platform compatibility

**Code Snippets (GitHub Gist):** [**02_intialize_git_create_essential_files**](https://gist.github.com/mikemurphyco/fb4b649daa1573074d2c926021312d91#file-02_intialize_git_create_essential_files)


```bash
# Initialize Git
git init

# Create comprehensive .gitignore
echo ".venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo ".vscode/" >> .gitignore
echo ".idea/" >> .gitignore
echo "*.DS_Store" >> .gitignore
echo "*.egg-info" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore

# Create .gitattributes for consistent line endings
echo "* text=auto" >> .gitattributes
echo "*.py text eol=lf" >> .gitattributes

# Initial commit
git add .gitignore .gitattributes
git commit -m "feat: Add .gitignore and .gitattributes"
```

### 3. Set Python Version

**Why:** Ensures a specific Python version is used for the project, preventing compatibility issues across different systems or updates.

**Best Practices:**
- Use `pyenv` for Python version management: `curl https://pyenv.run | bash`
- Set the desired Python version (e.g., 3.11) using `.python-version` file
- Verify the version matches your project requirements

**Code Snippets (GitHub Gist):** [**03_set_python_version**](https://gist.github.com/mikemurphyco/04a5da9f9528c3ef691684bf0c06b370#file-03_set_python_version)

```bash
# Set Python version for pyenv users (e.g., 3.11—adjust as needed)
echo "3.11" > .python-version

# Verify the Python version is available and active
python3 --version  # Should show 3.11.x if pyenv is working
```

### 4. Create and Activate Virtual Environment

**Why:** Isolates your project's dependencies from your system's global Python installation, preventing conflicts between different projects.

**Code Snippets (GitHub Gist):**[**04_create_activate_virtual_environment**](https://gist.github.com/mikemurphyco/e97d4f91b93a8ba8221af53d9b24f92a#file-04_create_activate_virtual_environment)

#### 📚 Traditional Workflow
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
# Windows: .venv\Scripts\activate.bat
```

#### 🚀 Modern Workflow (UV)
```bash
# UV handles virtual environments automatically with uv init
# But if you need manual control:
uv venv
source .venv/bin/activate  # Unix/macOS
```

### 5. Create Requirements Files

**Why:** These files ensure reproducibility by listing all packages and their versions your project needs.

**Best Practices:**
- `requirements.txt` for production dependencies
- `requirements-dev.txt` for development tools (testing, linting, formatting)
- Pin versions for reproducible builds

**Code Snippets (GitHub Gist):** [**05_create_requirements_files**](https://gist.github.com/mikemurphyco/4a1309ea75acde2120fed03fb5f91c79#file-05_create_requirements_files)


```bash
# Create empty requirements files
touch requirements.txt requirements-dev.txt

# Add to Git tracking
git add requirements.txt requirements-dev.txt
git commit -m "feat: Add empty requirements files"
```

### 6. Add Core Project Structure

**Why:** A well-defined structure makes your project easy to navigate and understand for both you and others.

**Best Practices:**
- Create a source directory with your project name
- Include essential documentation files
- Set up testing directory from the start
- Add environment variable template for configuration

**Code Snippets (GitHub Gist):** [**06_add_core_project_structure**](https://gist.github.com/mikemurphyco/badad04d57982210901992acf2e1c70a#file-06_add_core_project_structure)


```bash
# Create main project structure
mkdir my_project tests
touch my_project/__init__.py my_project/__main__.py
touch tests/__init__.py tests/test_my_project.py

# Create documentation and configuration files
touch README.md LICENSE pyproject.toml

# Create environment variable template
echo "# Copy to .env and fill in your values" >> .env.example
echo "OPENAI_API_KEY=your_key_here" >> .env.example
echo "DATABASE_URL=sqlite:///app.db" >> .env.example

# Add version to main package
echo '__version__ = "0.1.0"' >> my_project/__init__.py

# Add everything to Git
git add my_project/ tests/ README.md LICENSE .env.example pyproject.toml
git commit -m "feat: Add project structure and documentation templates"
```

### 7. Install Development Dependencies

**Why:** Installing linters, formatters, and testing tools upfront ensures consistent code quality from the beginning.

**Code Snippets (GitHub Gist):** [**07_install_development_dependencies**](https://gist.github.com/mikemurphyco/43b41d799a46a193064f639f1dbc91b4#file-07_install_development_dependencies)

#### 📚 Traditional Workflow
```bash
# Install essential development dependencies
pip install pytest pytest-cov black ruff pre-commit

# Update requirements-dev.txt
pip freeze > requirements-dev.txt
```

#### 🚀 Modern Workflow (UV)
```bash
# Install development dependencies (much faster)
uv add --dev pytest pytest-cov black ruff pre-commit

# Dependencies automatically tracked in pyproject.toml
```

#### Configuration (Both Workflows)
```bash
# Configure tools in pyproject.toml
cat <<EOF >> pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "W", "C", "I", "N"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=my_project --cov-report=html --cov-report=term-missing"
EOF

# Set up pre-commit hooks
pre-commit install

# Create .pre-commit-config.yaml
cat <<EOF > .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
EOF

# Run initial formatting and linting
black .
ruff check . --fix

# Commit configuration
git add pyproject.toml requirements-dev.txt .pre-commit-config.yaml
git commit -m "feat: Configure development tools and pre-commit hooks"
```

### 8. Create Sandbox Folder

**Why:** Provides a dedicated space for experimental code without cluttering the main project.

**Best Practices:**
- Use for quick prototypes, testing APIs, or data exploration
- Keep sandbox contents out of version control
- Include `.gitkeep` to track the folder structure

**Code Snippets (GitHub Gist):** [**08_create_sandbox_folder**](https://gist.github.com/mikemurphyco/54aabcf7a5a147c1e56251e26f32ee63#file-08_create_sandbox_folder)


```bash
# Create sandbox folder
mkdir sandbox
touch sandbox/.gitkeep

# Ignore sandbox contents but track the folder
echo "*" >> sandbox/.gitignore
echo "!.gitkeep" >> sandbox/.gitignore

# Add to Git
git add sandbox/
git commit -m "feat: Add sandbox folder for experiments"
```

### 9. Link to Remote Repository

**Why:** Provides cloud backup and enables collaboration with others.

**Best Practices:**
- Create repository on GitHub/GitLab first
- Use SSH keys for secure authentication
- Set up branch protection rules for production projects

**Code Snippets (GitHub Gist):** [**09_link_to_remote_repository**](https://gist.github.com/mikemurphyco/ded02c08772bfa10473ab1bf47cb3357#file-09_link_to_remote_repository)


```bash
# Replace with your repository URL
git remote add origin <repo-url>
git branch -M main
git push -u origin main
```

### 10. Verification & Testing

**Why:** Ensures all components are correctly configured and working together.

**Best Practices:**
- Verify virtual environment is active
- Test all development tools work correctly
- Run a complete test suite to ensure setup is functional

**Code Snippets (GitHub Gist):** [**10_verification_testing**](https://gist.github.com/mikemurphyco/1abf3061b7b88127cc3a5e6e94f70d7e#file-10_verification_testing)

```bash
# Verify virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❌ Virtual environment not active"
  echo "Run: source .venv/bin/activate"
  exit 1
else
  echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

# Check Python version
echo "🐍 Python version: $(python --version)"

# Verify dependencies
pip check && echo "✅ Dependencies OK"

# Create basic test file if needed
cat <<EOF > tests/test_my_project.py
import pytest
from my_project import __version__

def test_version():
    assert __version__ == "0.1.0"

def test_basic_import():
    import my_project
    assert my_project is not None
EOF

# Run code quality checks
echo "🔍 Running code quality checks..."
black --check . && echo "✅ Black formatting OK"
ruff check . && echo "✅ Ruff linting OK"

# Run tests
echo "🧪 Running tests..."
pytest && echo "✅ Tests passed"

# Check Git status
git status --porcelain
if [ $? -eq 0 ]; then
  echo "✅ Git status clean"
else
  echo "⚠️  Uncommitted changes detected"
fi

# Final commit if needed
git add tests/test_my_project.py
git commit -m "feat: Add basic tests and verify setup"

echo '🎉 Project setup complete and verified!'
```

---

## 🔗 UV Installation Guide

If you chose the Modern Workflow above, here's how to install UV:

### One-Time Setup
```bash
# macOS and Linux (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Using pip
pip install uv
```

### Why UV?
- **10-100x faster** than pip (3 seconds vs 30+ seconds for dependencies)
- **Auto-downloads Python versions** - no need for pyenv management
- **Creates complete project structure** - pyproject.toml, .gitignore, main.py, README.md
- **Modern dependency management** with lockfiles (uv.lock) for reproducible builds
- **All-in-one tool** replacing pip, pip-tools, virtualenv, pyenv, and more
- **Better dependency resolution** with clearer error messages
- **Compatible with existing pip workflows** when needed

### Project Templates

Consider using project templates for specific use cases:

- **CLI Tools:** `cookiecutter-pypackage`
- **Web Apps:** `cookiecutter-django` or `cookiecutter-fastapi`  
- **Data Science:** `cookiecutter-data-science`

```bash
pip install cookiecutter
cookiecutter https://github.com/audreyfeldroy/cookiecutter-pypackage.git
```

---

## 🔧 Troubleshooting

**Common Issues:**

1. **Virtual environment not activating**
   - Check path: `which python` should point to `.venv/bin/python`
   - Recreate: `rm -rf .venv && python3 -m venv .venv`

2. **Pre-commit hooks failing**
   - Run manually: `pre-commit run --all-files`
   - Update hooks: `pre-commit autoupdate`

3. **Import errors in tests**
   - Install project in development mode: `pip install -e .`
   - Check `PYTHONPATH` includes project root

4. **Git issues**
   - Set user info: `git config user.name "Your Name"`
   - Check remote: `git remote -v`

---

## 📝 Next Steps

After setup, consider:
- [ ] Write comprehensive README.md
- [ ] Add GitHub Actions for CI/CD
- [ ] Set up code coverage reporting
- [ ] Configure dependabot for security updates
- [ ] Add documentation with Sphinx or MkDocs
- [ ] Set up semantic versioning with `bump2version`

**Happy coding! 🐍**