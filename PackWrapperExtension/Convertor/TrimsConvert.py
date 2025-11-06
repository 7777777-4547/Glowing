from PackWrapperExtension.ExtensionLogger import ExtensionLogger
from PackWrapperExtension.Convertor import Utils

from PackWrapper.PathEnum import PackWrapper
from PackWrapper.Logger import Logger
from PackWrapper.Utils import Event, EventType

from pathlib import Path
from PIL import Image


class TrimsConvert():

    @ExtensionLogger.ID("TrimsConvert")
    def __init__(self, 
                 source_dir: str | Path, 
                 color_palettes_dir: str | Path,
                 **extra_properties):
                
        self.source_dir = Path(source_dir)
        self.export_dir = PackWrapper.EXPORT / self.source_dir.name
        self.color_palettes_dir = Path(color_palettes_dir)
        
        trim_palette_path = Path(color_palettes_dir, "trim_palette.png") if Path(color_palettes_dir, "trim_palette.png").exists() else None
        if trim_palette_path is None:
            Logger.exception("No trim palette found, please make sure you have a trim palette in the color_palettes directory.")
        else:
            self.trim_palette_path = trim_palette_path
        self.trim_palette_colored_list = [
            x for x in list(Path(color_palettes_dir).glob("*.png"))
            if x != trim_palette_path
        ]
        self.source_trims_list = [
            *list(Path(self.source_dir).glob("assets/minecraft/textures/trims/entity/**/*.png")),
            *list(Path(self.source_dir).glob("assets/minecraft/textures/trims/models/**/*.png")),
            *list(Path(self.source_dir).glob("assets/minecraft/textures/trims/items/**/*.png")),
            
            *list(Path(self.source_dir).glob("*/assets/minecraft/textures/trims/entity/**/*.png")),
            *list(Path(self.source_dir).glob("*/assets/minecraft/textures/trims/models/**/*.png")),
            *list(Path(self.source_dir).glob("*/assets/minecraft/textures/trims/items/**/*.png"))
        ]
                
        Logger.info("TrimsConvert initialized.")    
    
    @staticmethod
    def image_convert(temp_trim_image: Image.Image,
                      color_palette_image: Image.Image, 
                      temp_color_palette_image: Image.Image) -> Image.Image:
        
        temp_color_palette_image_data = list(temp_color_palette_image.getdata())
        color_palette_image_data = list(color_palette_image.getdata())
        
        new_trim_image = Image.new("RGBA", temp_trim_image.size)
        
        color_map = {} # dict[tuple[int, int, int, int], tuple[int, int, int, int]] 
            
        for temp_pixel_data, pixel_data in zip(temp_color_palette_image_data, color_palette_image_data):
            color_map[temp_pixel_data] = pixel_data
            
        for x in range(temp_trim_image.width):
            for y in range(temp_trim_image.height):
                temp_color = temp_trim_image.getpixel((x, y))
                if temp_color in color_map.keys():
                    new_trim_image.putpixel((x, y), color_map[temp_color])
        
        return new_trim_image
    
    @staticmethod
    def file_convert(temp_trim_file_path: str | Path,
                     color_palette_file_path: str | Path,
                     temp_color_palette_file_path: str | Path,
                     export_file_path: str | Path | None = None) -> None:
        
        temp_trim_image = Image.open(temp_trim_file_path).convert("RGBA")
        color_palette_image = Image.open(color_palette_file_path).convert("RGBA")
        temp_color_palette_image = Image.open(temp_color_palette_file_path).convert("RGBA")
        
        colored_trim_suffix = f"_{Path(color_palette_file_path).stem}_e"
        
        new_image = TrimsConvert.image_convert(temp_trim_image=temp_trim_image, 
                                               color_palette_image=color_palette_image, 
                                               temp_color_palette_image=temp_color_palette_image)
        
        if (export_file_path is None) or (export_file_path == temp_trim_file_path): 
            
            export_file_name = f"{Path(temp_trim_file_path).stem}{colored_trim_suffix}"
            export_file_path = Path(temp_trim_file_path).with_stem(export_file_name)
            Logger.warning(f"Wrong export path, change the export name to \"{export_file_name}\"")
        
        new_image.save(export_file_path)
    
    @ExtensionLogger.ID("TrimsConvert")
    def convert(self):
        
        Logger.info("Starting convert to trims...")
        #Logger.info("Waiting for the pack start exporting...")
        #Logger.info("The pack's exporting started, start convert...")
        
        for trim_palette_colored_file_path in self.trim_palette_colored_list:
            
            colored_trim_suffix = f"_{Path(trim_palette_colored_file_path).stem}_e"
            
            for trim_file_path in self.source_trims_list:
                                
                export_file_name = f"{Path(trim_file_path).stem}{colored_trim_suffix}"
                export_file_path = Utils.path_relative(Path(trim_file_path).with_stem(export_file_name), self.source_dir, self.export_dir)
                
                TrimsConvert.file_convert(
                    temp_trim_file_path = trim_file_path,
                    color_palette_file_path = trim_palette_colored_file_path, 
                    temp_color_palette_file_path = self.trim_palette_path,
                    export_file_path = export_file_path
                )
                
                export_original_file_path = Utils.path_relative(trim_file_path, self.source_dir, self.export_dir)
                Path(export_original_file_path).unlink(missing_ok=True)
                
    
        Logger.info("Convert completed.")                    
        
            
            
        
        
        
        
