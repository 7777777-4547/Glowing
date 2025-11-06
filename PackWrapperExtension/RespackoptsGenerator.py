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
 - change: file_presets(dict[str, list[str|Path]], like "<condition>": ["<file_path>","<file_path>])
 - change: compat_mode, to make sure that the pack default preset is same without mod installed.
'''




class OptionTypes:
    
    @staticmethod
    def num_slider(default: int|float, min: int|float, max: int|float):
        return {
            "type": "number_slider",
            "default": default,
            "min": min,
            "max": max
        }
    
    @staticmethod
    def num_slider_int(default: int, min: int, max: int):
        return {
            "type": "integer_slider",
            "default": default,
            "min": min,
            "max": max
        }
    
    @staticmethod
    def enum_list(default: str, values: list[str]):
        return {
            "type": "enum",
            "default": default,
            "values": values
        }
        
    @staticmethod
    def simple_list(values: list[str]):
        return values



'''

Respackopts docs: https://mods.jfronny.dev/Respackopts/setup/GettingStarted.html

μScript: https://git.jfronny.dev/Johannes/java-commons/src/branch/master/muscript-runtime/StandardLib.md

'''    

class RespackoptsGenerator():
        
    class ConfigRegister:
        
        option_types: TypeAlias = Literal["string", "boolean", "number", "integer", "list", "enum"]
        reload_types: TypeAlias = Literal["Simple", "Resource"]
        
        _conf = {}
        
        @staticmethod
        def type_check(option_type: option_types, value1: str | bool | int | float | list, value2: list[str] | None = None):
            
            value1_type = type(value1)
            value2_type = type(value2)
            
            if option_type == "string":
                if not isinstance(value1, str):
                    Logger.exception(f"Expected string, got {value1_type}", exc_info=TypeError)
                
            elif option_type == "boolean":
                if not isinstance(value1, bool):
                    Logger.exception(f"Expected boolean, got {value1_type}", exc_info=TypeError)
            
            elif option_type == "number":
                if not isinstance(value1, (int, float)):
                    Logger.exception(f"Expected number(int, float), got {value1_type}", exc_info=TypeError)
                                
            elif option_type == "integer":
                if not isinstance(value1, int):
                    Logger.exception(f"Expected integer(int), got {value1_type}", exc_info=TypeError)
            
            elif option_type == "list":
                if not isinstance(value1, list):
                    Logger.exception(f"Expected list, got {value1_type}", exc_info=TypeError)
                    
            elif option_type == "enum":
                if not (isinstance(value1, str) and isinstance(value2, list)):
                    Logger.exception(f"Expected enum(str+list[str]), got {value1_type} and {value2_type}", exc_info=TypeError)
   
        
        @classmethod
        def new_option(cls, 
                       name: str, 
                       type: option_types,
                       default: str | bool | int | float | list, 
                       min: float | None = None,
                       max: float | None = None,
                       values: list | None = None,
                       reload_type: reload_types | None = None) -> dict[str, Any]:
            
            cls.type_check(type, default, values)
            
            if type == "string":
                cls._conf[name] = {
                    "type":"string",
                    "default": default

                }
                            
            if type == "boolean":
                if reload_type is None:
                    cls._conf[name] = default
                else:
                    cls._conf[name] = {
                        "type":"boolean",
                        "default": default, 
                        "reload_type": reload_type
                    }

            if (type == "number") and (min is not None) and (max is not None):
                cls._conf[name] = {
                    "type":"number",
                    "default": default,
                    "min": min,
                    "max": max
                } if reload_type is None else {
                    "type":"number",
                    "default": default,
                    "min": min,
                    "max": max,
                    "reload_type": reload_type
                }
            else:
                cls._conf[name] = default
            
            if type == "integer":
                
                if min is None or max is None:
                    Logger.exception("Expected min and max for integer", exc_info=TypeError)
                elif min > max:
                    Logger.exception("\"min\" must be less than \"max\"", exc_info=TypeError)
                
                cls._conf[name] = {
                    "type":"integer",
                    "default": default,
                    "min": min,
                    "max": max
                } if reload_type is None else {
                    "type":"integer",
                    "default": default,
                    "min": min,
                    "max": max,
                    "reload_type": reload_type
                }
            
            
            if type == "enum":
                cls._conf[name] = {
                    "type":"enum",
                    "default": default,
                    "values": values
                } if reload_type is None else {
                    "type":"enum",
                    "default": default,
                    "values": values,
                    "reload_type": reload_type
                }
            
            if type == "list":
                cls._conf[name] = default
                
            return {name: copy.deepcopy(cls._conf[name])}


        @classmethod
        def new_category(cls, name: str, *options):
            cls._conf[name] = {
                *options
            }
            return {name: copy.deepcopy(cls._conf[name])}
        
        
        def get_conf(self):
            return copy.deepcopy(self._conf)
            
                
                
        
    
    
    
    
        
    def __init__(self,
                 pack_properties: dict,
                 id, 
                 version, 
                 capabilities, 
                 conf: dict
                 ):
        
        self.pack_properties = pack_properties
        self.rpo_properties = pack_properties["respackopts"]
        self.source_dir = Path(pack_properties["source_dir"])
        
        self.id = id
        self.version = version
        self.capabilities = capabilities
        self.conf = conf
        
        self.rpo_main = {
            "id": id,
            "version": version,
            "capabilities": capabilities,
            "conf": {**conf}
        }
        
        self.rpo_conditions: dict[str, list[str | Path] | str | Path] = {}
    
    # <condition>: [file1, file2]  
    
    def condition(self, condition: dict[str, list[str | Path] | str | Path]):
        self.rpo_conditions.update(condition)
    
    def conditions(self, **condition: list[str | Path] | str | Path):
        self.rpo_conditions.update(condition)
    
    def conditions_advanced(self):
        #TODO: Not yet.
        pass
    
    def __generate(self):
        cache_dir = PackWrapper.CACHE / self.source_dir.name
        
        try:
            with open(cache_dir / "respackopts.json5" , mode="w") as f:
                json5.dump(self.rpo_main, f, indent=4)
        
        except Exception:
            Logger.exception(f"Failed to generate resourcepack options")
        
        
        try:
            for condition, files_or_dirs in self.rpo_conditions.items():
                
                option = {
                    "condition": condition
                } 
                
                if isinstance(files_or_dirs, list):
                    for file_or_dir in files_or_dirs:
                        
                        rel_path = Path(file_or_dir).relative_to(self.source_dir)
                        dest_path = cache_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(cache_dir / f"{dest_path}.rpo", mode="w") as f:
                            json.dump(option, f, indent=4)
                            
                else:
                    
                    rel_path = Path(files_or_dirs).relative_to(self.source_dir)
                    dest_path = cache_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(cache_dir / f"{dest_path.parent}" / ".rpo", mode="w") as f:
                        json.dump(option, f, indent=4)
        
        except Exception:
            Logger.exception(f"Failed to generate resourcepack options")
    

@deprecated("Not done yet.")
class RespackoptsGeneratorAuto(RespackoptsGenerator):
    
    def __init__(self, properties: dict):
        super().__init__(properties, **properties["respackopts"])