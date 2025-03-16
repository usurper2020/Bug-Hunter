import os
import zipfile
from datetime import datetime
from pathlib import Path

def create_backup(files, script_name):
    """Create a compressed backup of files"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = backup_dir / f"{script_name}_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in files:
            # Convert to absolute path if necessary
            abs_path = Path(file_path).absolute()
            # Create relative path for archive
            arcname = abs_path.relative_to(Path.cwd().absolute())
            zipf.write(abs_path, arcname)
    
    return zip_path
