from pathlib import Path
from platformdirs import PlatformDirs

# Load platform-specific directories

# --- User data ----
_platform_dirs = PlatformDirs("HapticPancake", "BitFoxDen")
PATH_USER_DATA = _platform_dirs.user_data_dir

# Ensure all paths exist
# See https://stackoverflow.com/questions/273192/how-do-i-create-a-directory-and-any-missing-parent-directories
Path(PATH_USER_DATA).mkdir(parents=True, exist_ok=True)
