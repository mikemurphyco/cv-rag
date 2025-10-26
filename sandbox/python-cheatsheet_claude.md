Python Virtual Environment Cheatsheet (Mac)

  ✅ Standard venv (What We're Using)

  Initial Setup (One Time Per Project)

  # Navigate to project
  cd /path/to/your/project

  # Create venv (choose ONE name and stick with it)
  python3 -m venv .venv        # ← Recommended (hidden folder)
  # OR
  python3 -m venv venv         # ← Also common (visible folder)

  # Activate it
  source .venv/bin/activate    # If you used .venv
  # OR
  source venv/bin/activate     # If you used venv

  Daily Usage (Every Time You Work)

  # 1. Navigate to project
  cd /path/to/your/project

  # 2. Activate venv
  source .venv/bin/activate    # (or venv/bin/activate)

  # 3. Verify it's active
  which python                 # Should show: /path/to/project/.venv/bin/python

  # 4. Now use plain python/pip (NOT python3/pip3!)
  python script.py             # ✅ Correct
  pip install package          # ✅ Correct

  # 5. When done for the day
  deactivate

  ---
  🎯 The Rules (When venv is Active)

  | Command | When Active? | What to Use                    |
  |---------|--------------|--------------------------------|
  | python  | ✅ YES        | python (points to venv Python) |
  | pip     | ✅ YES        | pip (installs to venv)         |
  | python3 | ✅ YES        | ❌ DON'T USE (bypasses venv!)   |
  | pip3    | ✅ YES        | ❌ DON'T USE (bypasses venv!)   |

  | Command | When NOT Active? | What to Use                        |
  |---------|------------------|------------------------------------|
  | python  | ❌ NO             | May not work or uses system Python |
  | pip     | ❌ NO             | May install to system (bad!)       |
  | python3 | ❌ NO             | ✅ Use for creating venv only       |
  | pip3    | ❌ NO             | ✅ Use for global tools only        |

  ---
  🔍 How to Tell If venv Is Active

  Visual Cue

  # Active - see (venv-name) in prompt
  (cv-rag) mikemurphy@Mikes-M1-Max cv-rag %

  # NOT Active - no parentheses
  mikemurphy@Mikes-M1-Max cv-rag %

  Verification Command

  which python

  # ✅ Active (correct):
  /Users/mikemurphy/Code/Projects/cv-rag/.venv/bin/python

  # ❌ NOT Active (wrong):
  /usr/bin/python
  /opt/homebrew/bin/python3

  ---
  🚨 Common Mistakes & Fixes

  Mistake 1: Using python3 When Active

  # ❌ Wrong
  (cv-rag) % python3 script.py        # Bypasses venv!

  # ✅ Right
  (cv-rag) % python script.py         # Uses venv Python

  Mistake 2: Forgetting to Activate

  # You see this error:
  ModuleNotFoundError: No module named 'langchain_text_splitters'

  # Solution:
  source .venv/bin/activate
  python script.py                    # Now it works!

  Mistake 3: Wrong venv Name

  # You created .venv but try to activate venv
  source venv/bin/activate            # Error: No such file

  # Fix: Use the name you created
  source .venv/bin/activate           # ✅

  Mistake 4: Multiple venvs (UV + Standard)

  # You have BOTH .venv (UV) and venv (standard) folders
  # This causes confusion!

  # Solution: Delete one
  rm -rf venv                         # If keeping .venv
  # OR
  rm -rf .venv                        # If keeping venv

  # Then recreate fresh:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

  ---
  📋 Quick Reference Card

  # START OF DAY
  cd my-project
  source .venv/bin/activate
  which python                 # Verify it worked

  # WORKING
  python script.py             # Run scripts
  pip install package          # Install packages
  pip list                     # See what's installed

  # END OF DAY
  deactivate

  ---
  🆚 .venv vs venv (Which Name?)

  Both work, but pick ONE:

  | Name  | Pros                                     | Cons                     |
  |-------|------------------------------------------|--------------------------|
  | .venv | Hidden (cleaner), standard in many tools | Harder to see in ls      |
  | venv  | Visible, obvious it's there              | Clutters folder listings |

  Recommendation: Use .venv (what we're using in cv-rag)

  ---
  🔧 Troubleshooting Checklist

  If commands aren't working:

  1. ✅ Is venv active? Check for (venv-name) in prompt
  2. ✅ Did you activate with correct name? .venv vs venv
  3. ✅ Are you using python not python3?
  4. ✅ Is which python showing the venv path?
  5. ✅ Did you install packages AFTER activating?

  Nuclear option (start fresh):
  deactivate
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

  ---
  🚀 Pro Tips

  1. Add to .gitignore: Always ignore venv folders
  .venv/
  venv/
  2. VS Code: Select the venv Python interpreter
    - Cmd+Shift+P → "Python: Select Interpreter"
    - Choose the one with .venv in path
  3. requirements.txt: Always install from this when fresh
  pip install -r requirements.txt
  4. Save dependencies: After installing new packages
  pip freeze > requirements.txt
  5. Check what's installed:
  pip list | grep package-name

  ---
  ⚡ UV vs Standard venv (Quick Comparison)

  | Feature    | Standard venv             | UV                      |
  |------------|---------------------------|-------------------------|
  | Create     | python3 -m venv .venv     | uv venv                 |
  | Activate   | source .venv/bin/activate | Same                    |
  | Install    | pip install package       | uv pip install package  |
  | Run        | python script.py          | uv run python script.py |
  | Speed      | Normal                    | 10-100x faster          |
  | Complexity | Simple                    | Extra tool to learn     |

  For cv-rag: We're using standard venv (simpler, widely understood)

  ---
  Save this somewhere! Print it, bookmark it, tattoo it on your arm - whatever works! 😄