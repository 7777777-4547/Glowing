from PackWrapper.PathEnum import PackWrapper
from PackWrapper.Logger import Logger
from PackWrapper.Utils import Event, EventType

from typing import Any, Literal, TypeAlias
from warnings import deprecated
from pathlib import Path
import json5
import copy
import json

'''
TODO: 
 - change: Read the `respackopts.json5`
 - change: file_presets(dict[str, list[str|Path|dict[str, str]]], like "<condition>": ["<file_path>", {"<file_path>":"<fallback_file_path>"}])
 - change: compat_mode, to make sure that the pack default preset is same without mod installed.
'''

# TODO: older respackopts version support.
class RespackoptsGenerate():
    
    RPO_FILE_SUFFIX = ".rpo"
    
    test = {"file":("condition",["fallbacks"])}
    
    PresetsOriginal = dict[str, list[str|dict[str, str|list[str]]]]
    
    
    # Respackopts docs: https://mods.jfronny.dev/Respackopts/setup/GettingStarted.html
    
    # version 8+
    def __init__(self, source_dir: str | Path, presets: dict[str, list[str|dict[str, str|list[str]]]]):
        
        with open(Path(source_dir, "respackopts.json5"), "r") as file:
            self.configuration = json5.load(file)
        
        self.conf = self.configuration.get("conf", {})
        self.presets_original = presets
        
        # {"condition":{"file_path":"fallback_file_path"}}
        #self.presets_all: dict[str|Path, dict[str, str|Path|list[str]|None]] = {}
        self.presets_all: dict[str|Path, tuple[str, str|list[str]|None]] = {}
        
        for condition, _files_or_dirs in self.presets_original.items():
            
            file_or_dirs: list[str|Path|dict[str, str|list[str]]] = []
            
            for _file_or_dir in _files_or_dirs:
                
                if isinstance(_file_or_dir, str):
                    file_or_dirs += list(Path(source_dir).glob(_file_or_dir))
                
                elif isinstance(_file_or_dir, dict):
                    for _file_or_dir, fallback_files_or_dirs in _file_or_dir.items():
                        file_or_dirs.append({_file_or_dir: fallback_files_or_dirs})
                
            
            for file_or_dir in file_or_dirs:
                
                if isinstance(file_or_dir, str|Path):
                    self.presets_all[file_or_dir] = (condition, None)
                    
                if isinstance(file_or_dir, dict):
                    _main_file_or_dir = list(file_or_dir.keys())[0]
                    _fallback_files_or_dirs = list(file_or_dir.values())[0]
                    
                    if isinstance(_fallback_files_or_dirs, list):
                        for _fallback_file_or_dir in _fallback_files_or_dirs:
                            self._same_path_type_check(_main_file_or_dir, _fallback_file_or_dir)
                    else:
                        self._same_path_type_check(_main_file_or_dir, _fallback_files_or_dirs)
                                    
                    self.presets_all[_main_file_or_dir] = (condition, _fallback_files_or_dirs)
            
    @staticmethod
    def _same_path_type_check(path1: Path|str, path2: Path|str) -> bool:
        
        result = (Path(path1).is_file(), Path(path1).is_dir()) == (Path(path2).is_file(), Path(path2).is_dir())
        
        if not result:
            Logger.exception(f"{path1} and {path2} are not the same path type.", exc_info = Exception(f"{path1} and {path2} are not the same path type."))
        
        return result
        
        
    def generate(self):
        
        for file_or_dir, (condition, fallback_files_or_dirs) in self.presets_all.items():
            
            if Path(file_or_dir).is_file():
                
                _file_rpo_path = Path(file_or_dir).with_suffix(f"{Path(file_or_dir).suffix}{self.RPO_FILE_SUFFIX}")
                _rpo_preset = {
                    "condition": condition
                } if fallback_files_or_dirs is None else {
                    "condition": condition,
                    "fallback": fallback_files_or_dirs
                }

            elif Path(file_or_dir).is_dir():
                
                _dir_rpo_path = Path(file_or_dir, self.RPO_FILE_SUFFIX)
                _rpo_preset = {
                    "condition": condition
                } if fallback_files_or_dirs is None else {
                    "condition": condition,
                    "fallback": fallback_files_or_dirs
                }

            
        
        
        

        
        