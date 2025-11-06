from PackWrapperExtension.Convertor.TrimsConvert import TrimsConvert
from PackWrapperExtension.ExtensionLogger import ExtensionLogger
from PackWrapperExtension.Convertor import Utils

from PackWrapper.PathEnum import PackWrapper
from PackWrapper.Logger import Logger
from PackWrapper.Utils import Event, EventType

from collections import defaultdict
from warnings import deprecated
from pathlib import Path
from typing import TypeAlias, Literal
from PIL import Image, ImageEnhance
import shutil
import copy


class PBRConvert():
    
    
    PBR_SUFFIX = "_s"
    
    PBRConvertModes: TypeAlias = Literal["default", "whitelist", "blacklist"]
    
    # ((red_weight, green_weight, blue_weight), emissive_weight, contrast_factor)
    PBRPresetType = tuple[tuple[float, float, float], float, float]
    
    
    class TrimsCompatibility:
        
        PBRPresetType = tuple[tuple[float, float, float], float, float]
        
        _preset: PBRPresetType = ((0.3, 0.59, 0.11), 1, 1)
        _temp_trims_file_preset: dict[Path|str, PBRPresetType] = {}
        
        @classmethod
        def preset(cls, preset: PBRPresetType):
            
            cls._preset = preset
            
        @classmethod
        def check(cls, path: str | Path) -> bool:
        
            if "trims" in Path(path).parts:
                cls._temp_trims_file_preset[path] = cls._preset
                return True
            else:
                return False
            
        @classmethod
        def get_preset(cls):
            return copy.deepcopy(cls._temp_trims_file_preset)
        
    @ExtensionLogger.ID("PBRConvert")                    
    def __init__(self, 
                 source_dir: str | Path, 
                 mode: PBRConvertModes = "default", 
                 preset_main: PBRPresetType | list[list[float] | float] = ((0.3, 0.59, 0.11), 1, 1), 
                 preset_custom: dict[str|Path, PBRPresetType] | None = None, 
                 match_list: list[str | Path] | None = None, 
                 **extra_properties):
                        
        self.source_dir = Path(source_dir)
        self.export_dir = PackWrapper.EXPORT / self.source_dir.name
        self.pbr_suffix = PBRConvert.PBR_SUFFIX
        
        self.mode = mode
        _preset_main = Utils.list_to_tuple(preset_main)
        self.preset_main = _preset_main
        
        self.preset_custom = preset_custom
        self.preset_all: dict[PBRConvert.PBRPresetType, list[Path]] = {}
        
        self.list_match_original = match_list # "/*/**/.."
        self.list_match_main = []
        self.list_file: list[Path] = []
                
        Logger.info(f"Mode: \"{mode}\"")
        
        if (mode == "whitelist") or (mode == "blacklist"):
            
            if match_list is None:
                Logger.exception("\"match_list\" is empty!")
            else:
                
                for match_file_or_dir in map(str, match_list):
                    
                    self.list_match_main = self.list_match_main + list((self.source_dir).glob(f"{match_file_or_dir}"))
                
                for matched_file_or_dir in map(Path, self.list_match_main):
                                        
                    if matched_file_or_dir.is_file() and (Path(matched_file_or_dir).suffix == ".png"):
                        self.list_file.append(matched_file_or_dir)
                    elif matched_file_or_dir.is_dir():
                        self.list_file = self.list_file + list((matched_file_or_dir).glob("**/*.png"))        
        
        elif mode == "default":
            
            self.preset_custom = preset_custom = {} if preset_custom is None else preset_custom
            _preset_custom: dict[PBRConvert.PBRPresetType, list[Path]] = defaultdict(list[Path])
            matched_files = []
            
            for match_file_or_dir, preset in self.preset_custom.items():
                
                preset_matched_files: list[Path] = []
                matched_files_or_dirs = list((self.source_dir).glob(f"{match_file_or_dir}"))
                
                for matched_file_or_dir in matched_files_or_dirs:
                                        
                    if matched_file_or_dir.is_file() and (Path(matched_file_or_dir).suffix == ".png"):
                        preset_matched_files.append(matched_file_or_dir)
                    elif matched_file_or_dir.is_dir():
                        preset_matched_files = preset_matched_files + list((matched_file_or_dir).glob("**/*.png"))
                
                self.TrimsCompatibility.preset(preset)
                map(self.TrimsCompatibility.check, preset_matched_files)
                                                
                _preset_custom[Utils.list_to_tuple(preset)].extend(preset_matched_files)
                
                matched_files += preset_matched_files
            
            _preset_custom = {k: v for k, v in _preset_custom.items() if k not in self.TrimsCompatibility.get_preset().keys()}
                        
            self.TrimsCompatibility.preset(self.preset_main)
            self.preset_all[self.preset_main] = list(Path(source_dir).glob("**/*.png"))
                        
                        
            ''' 
            for x in self.preset_all[self.preset_main]:
                                
                if x in matched_files:
                    self.preset_all[self.preset_main].remove(x)
                    
                if self.TrimsCompatibility.check(x):
                    self.preset_all[self.preset_main].remove(x)
            '''
                      
            self.preset_all[self.preset_main] = [x for x in self.preset_all[self.preset_main] if not (x in matched_files or self.TrimsCompatibility.check(x))]
            #self.preset_all.update(_preset_custom)
            
            for preset, files in _preset_custom.items():
                if preset in self.preset_all:
                    self.preset_all[preset] = list(dict.fromkeys(self.preset_all[preset] + files))
                else:
                    self.preset_all[preset] = files
            
                        

        if mode == "blacklist":
            list_file_all = list(Path(source_dir).glob("**/*.png"))
            list_file_ = self.list_file
            list_file_filtered = [x for x in list_file_all if x not in list_file_]
            self.list_file = list_file_filtered
            
            self.TrimsCompatibility.preset(self.preset_main)
            map(self.TrimsCompatibility.check, list_file_filtered)
            
            self.list_file = [x for x in self.list_file if not self.TrimsCompatibility.check(x)]            
        
        elif mode == "whitelist":
            
            self.TrimsCompatibility.preset(self.preset_main)
            map(self.TrimsCompatibility.check, self.list_file)
            
            self.list_file = [x for x in self.list_file if not self.TrimsCompatibility.check(x)]
        
        
        Logger.info("PBRConvert initialized.")    
    
    @deprecated("Deprecated")        
    def auto_subscribe(self, data = None, data_verification = None , event: EventType | None = None):
        if event is None:
            raise
        Event.subscribe(event, self.auto_subscribe)
        if data != data_verification:
            Event.subscribe(event, self.auto_subscribe)
        else:
            return True
    
        
    @staticmethod
    def _mcmeta_check(file_path: str | Path):
        if Path(f"{file_path}.mcmeta").exists():
            return True
        else:
            return False


    @staticmethod
    def alpha0_locker(source_image: Image.Image):
        image_data = list(source_image.getdata())
        new_image_data = []
        
        for pixel_data in image_data:
            if pixel_data[3] == 0:
                new_image_data.append((0, 0, 0, 0))
            else:
                new_image_data.append((255, 255, 255, 255))
        
        new_image = Image.new(source_image.mode, source_image.size)
        new_image.putdata(new_image_data)
        
        return new_image
    
    @staticmethod
    def image_convert(source_image: Image.Image, 
                      channel_weight: tuple[float, float, float] = (0.3, 0.59, 0.11), 
                      e_level_weight: float = 1, 
                      contrast_factor: float = 1) -> Image.Image:
        '''
        `channel_weight`: (r, g, b), the weight of each color channel to transform, default is (0.3, 0.59, 0.11)\n
        `e_level_weight`: the weight of emissive level, default is 1\n
        `contrast_factor`: the factor of contrast, default is 1\n
        '''
        
        alpha0_image_data = list(PBRConvert.alpha0_locker(source_image).getdata())
        
        _image = ImageEnhance.Contrast(source_image).enhance(contrast_factor)
        
        _image_data = list(_image.getdata())
        
        _new_image_data = []
        
        for pixel_data, alpha0_pixel_data in zip(_image_data, alpha0_image_data):
            if pixel_data[3] != alpha0_pixel_data[3]:
                _new_image_data.append(alpha0_pixel_data)
            else:
                _new_image_data.append(pixel_data)
        
        new_image_data = []
        
        for pixel_data in _image_data:

            r, g, b, a = pixel_data
            rw, gw, bw = channel_weight

            if a == 0:
                new_image_data.append(pixel_data)
            else:
                pixel_data_e_level = int(sum((r*rw, g*gw, b*bw)) * e_level_weight) - 1   # emissive level transform
                new_image_data.append((0, 0, 0, pixel_data_e_level if pixel_data_e_level < 255 else 254))
        
        new_image = Image.new(source_image.mode, source_image.size)
        new_image.putdata(new_image_data)
                
        return new_image
    
    @staticmethod
    def image_convert_avg(source_image: Image.Image, 
                          channel_weight: tuple[float, float, float] = (0.3, 0.59, 0.11), 
                          e_level_weight: float = 1,
                          contrast_factor: float = 1) -> Image.Image:
        '''
        `channel_weight`: (r, g, b), the weight of each color channel to transform, default is (0.3, 0.59, 0.11)\n
        `e_level_weight`: the weight of emissive level, default is 1\n
        `contrast_factor`: the factor of contrast, default is 1\n
        '''

        alpha0_image_data = list(PBRConvert.alpha0_locker(source_image).getdata())
        
        _image = ImageEnhance.Contrast(source_image).enhance(contrast_factor)
        
        _image_data = list(_image.getdata())
        
        _new_image_data = []
        
        for pixel_data, alpha0_pixel_data in zip(_image_data, alpha0_image_data):
            if pixel_data[3] != alpha0_pixel_data[3]:
                _new_image_data.append(alpha0_pixel_data)
            else:
                _new_image_data.append(pixel_data)
        
        
        pixel_data_e_level = 0
        pixel_data_e_lens = 0
        
        rw, gw, bw = channel_weight
        
        for pixel_data in _new_image_data:

            r, g, b, a = pixel_data

            if a != 0:
                pixel_data_e_level += int(sum((r*rw, g*gw, b*bw)) * e_level_weight) - 1   # emissive level transform
                pixel_data_e_lens += 1
            
        pixel_data_e_level = pixel_data_e_level // pixel_data_e_lens
        
        
        new_image_data = []
        
        for pixel_data in _new_image_data:
            
            _, _, _, a = pixel_data
            
            
            if a == 0:
                new_image_data.append(pixel_data)
            else:
                new_image_data.append((0, 0, 0, pixel_data_e_level if pixel_data_e_level < 255 else 254))
                
        
        new_image = Image.new(source_image.mode, source_image.size)
        new_image.putdata(new_image_data)
        
        return new_image
    
    @staticmethod
    def file_convert(source_file_path: str | Path, 
                     export_file_path: str | Path | None = None,
                     channel_weight: tuple[float, float, float] = (0.3, 0.59, 0.11), 
                     e_level_weight: float = 1, 
                     contrast_factor: float = 1) -> None:
        
        source_file_name = Path(source_file_path).stem
        
        image = Image.open(source_file_path).convert("RGBA")
        new_image = PBRConvert.image_convert(image, channel_weight, e_level_weight, contrast_factor)
        
        if (export_file_path is None) or (export_file_path == source_file_path):
           
            export_file_name = f"{source_file_name}{PBRConvert.PBR_SUFFIX}"
            export_file_path = Path(source_file_path).with_stem(export_file_name)
            Logger.warning(f"Wrong export path, change the export name to \"{export_file_name}\"")
                    
        new_image.save(export_file_path)
        
    @staticmethod
    def file_convert_avg(source_file_path: str | Path, 
                         export_file_path: str | Path | None = None,
                         channel_weight: tuple[float, float, float] = (0.3, 0.59, 0.11), 
                         e_level_weight: float = 1, 
                         contrast_factor: float = 1) -> None:
        
        source_file_name = Path(source_file_path).stem
        
        image = Image.open(source_file_path).convert("RGBA")
        new_image = PBRConvert.image_convert_avg(image, channel_weight, e_level_weight, contrast_factor)
        
        if (export_file_path is None) or (export_file_path == source_file_path):
           
            export_file_name = f"{source_file_name}{PBRConvert.PBR_SUFFIX}"
            export_file_path = Path(source_file_path).with_stem(export_file_name)
            Logger.warning(f"Wrong export path, change the export name to \"{export_file_name}\"")
                    
        new_image.save(export_file_path)
        
    @staticmethod
    def trims_file_convert(color_palette_file_path: str | Path, 
                           temp_color_palette_file_path: str | Path,
                           source_file_path: str | Path,
                           export_file_path: str | Path | None = None,
                           channel_weight: tuple[float, float, float] = (0.3, 0.59, 0.11), 
                           e_level_weight: float = 1, 
                           contrast_factor: float = 1) -> None:
        
        source_file_name = Path(source_file_path).stem
        
        temp_trim_image = Image.open(source_file_path).convert("RGBA")
        color_palette_image = Image.open(color_palette_file_path).convert("RGBA")
        temp_color_palette_image = Image.open(temp_color_palette_file_path).convert("RGBA")
        
        colored_trim_suffix = f"_{Path(color_palette_file_path).stem}_e"        
        
        new_trim_image = TrimsConvert.image_convert(temp_trim_image=temp_trim_image, 
                                                    color_palette_image=color_palette_image,
                                                    temp_color_palette_image=temp_color_palette_image)
        
        new_trim_pbr_image = PBRConvert.image_convert(new_trim_image, channel_weight, e_level_weight, contrast_factor)
        
        if (export_file_path is None) or (export_file_path == source_file_path):
           
            export_file_name = f"{source_file_name}{colored_trim_suffix}{PBRConvert.PBR_SUFFIX}"
            export_file_path = Path(source_file_path).with_stem(export_file_name)
            Logger.warning(f"Wrong export path, change the export name to \"{export_file_name}\"")

        new_trim_pbr_image.save(export_file_path)
    
    @staticmethod
    def _convert_normal(file_path: Path, 
                        source_dir: Path, 
                        export_dir: Path, 
                        channel_weight: tuple[float, float, float], 
                        e_level_weight: float, 
                        contrast_factor: float):

        if e_level_weight == 0:
            return
        
        if PBRConvert._mcmeta_check(file_path):
            
            file_mcmeta_path = Path(f"{file_path}.mcmeta")
            file_mcmeta_export_path = Path(file_mcmeta_path).with_stem(f"{file_path.stem}{PBRConvert.PBR_SUFFIX}.png")
            file_mcmeta_export_path = Utils.path_relative(file_mcmeta_export_path, source_dir, export_dir)
            
            shutil.copy2(file_mcmeta_path, file_mcmeta_export_path)
                
            file_export_path = Path(file_path).with_stem(f"{file_path.stem}{PBRConvert.PBR_SUFFIX}")
            file_export_path = Utils.path_relative(file_export_path, source_dir, export_dir)
            PBRConvert.file_convert_avg(file_path, file_export_path, channel_weight, e_level_weight, contrast_factor)
            
        else:
            file_export_path = Path(file_path).with_stem(f"{file_path.stem}{PBRConvert.PBR_SUFFIX}")
            file_export_path = Utils.path_relative(file_export_path, source_dir, export_dir)
            PBRConvert.file_convert(file_path, file_export_path, channel_weight, e_level_weight, contrast_factor)
        
    @ExtensionLogger.ID("PBRConvert")
    def convert(self, 
                trims_compat = False,
                color_palettes_dir: str | Path | None = None):
        

        Logger.info("Starting convert to PBR...")
        #Logger.info("Waiting for the pack start exporting...")
        #Logger.info("The pack's exporting detected, starting to convert...")
        
        if (self.mode == "whitelist") or (self.mode == "blacklist"):
            for file_path in self.list_file:
                
                self._convert_normal(file_path, self.source_dir, self.export_dir, 
                                     self.preset_main[0], self.preset_main[1], self.preset_main[2])
                            
        else:
            for preset, files in self.preset_all.items():
                for file_path in map(Path, files):
                    
                    self._convert_normal(file_path, self.source_dir, self.export_dir, 
                                         preset[0], preset[1], preset[2])
                    
        
        if trims_compat == True:
            
            if color_palettes_dir is None:
                Logger.exception("No color palettes directory provided, please make sure you have a color palettes directory in the source directory.")
            else:
                trim_palette_path = Path(color_palettes_dir, "trim_palette.png") if Path(color_palettes_dir, "trim_palette.png").exists() else None
                
                if trim_palette_path is None:
                    Logger.exception("No trim palette found, please make sure you have a trim palette in the color_palettes directory.")
                    raise
                    
                trim_palette_colored_list = [
                    x for x in list(Path(color_palettes_dir).glob("*.png"))
                    if x != trim_palette_path
                ]                
                
                for trim_palette_colored_file_path in trim_palette_colored_list:
                                              
                    colored_trim_suffix = f"_{Path(trim_palette_colored_file_path).stem}_e"        
                    
                    for trim_file_path, preset in self.TrimsCompatibility.get_preset().items():
                        
                        _export_path = Path(trim_file_path).with_stem(f"{Path(trim_file_path).stem}{colored_trim_suffix}{PBRConvert.PBR_SUFFIX}")
                        export_path = Utils.path_relative(_export_path, self.source_dir, self.export_dir)
                        
                        PBRConvert.trims_file_convert(
                            color_palette_file_path = trim_palette_colored_file_path,
                            temp_color_palette_file_path = trim_palette_path, 
                            source_file_path = trim_file_path,
                            export_file_path = export_path,
                            channel_weight = preset[0],
                            e_level_weight= preset[1]
                        )
            
            
            Logger.info("Convert completed.")