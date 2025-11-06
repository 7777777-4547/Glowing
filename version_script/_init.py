import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from PackWrapper import PropertiesManager

def config_read(file_path):
    PropertiesManager.properties_read(os.path.join(os.path.dirname(__file__), file_path))
    
def get_config():
    args = sys.argv[1:]
    if 0 < len(args):
        return args[0]
    raise ValueError(f"No argument provided, it needs one")


from collections import Counter
from pathlib import Path
from PIL import Image

def convert_to_P(source_file_path: Path, export_file_path: Path):
    
    image = Image.open(source_file_path)
    image_copy = image.copy().convert("RGBA")
    
    original_dpi = image.info.get('dpi', (72, 72))
    colors_counter = Counter(image_copy.getdata())
    unique_colors = len(colors_counter)
        
    if unique_colors > 256:
        return
    
    image = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=unique_colors)
    
    image.save(export_file_path, dpi = original_dpi)
