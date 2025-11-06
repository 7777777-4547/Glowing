import _init

import PackWrapper as PW
from PackWrapper.ScriptSystem import script_logger_config
from PackWrapper.Logger import Logger

import PackWrapperExtension as PWE
from PackWrapperExtension import Convertor

from pathlib import Path
import json


config = json.loads(_init.get_config())
script_logger_config(config.get("packwrapper", {}).get("debug_mode",False))

Logger.info("Reading config...")
Logger.debug(json.dumps(config, indent=4))
packinfo = config["pack_info"]


config_convertor = config["convertor"]


rp = PW.Resourcepack(**packinfo)
rp.export(export_name = packinfo.get("export_name", None))

Convertor.PBRConvert(source_dir=packinfo["source_dir"], **config_convertor["pbr"]).convert()

Logger.info("Converting to 'P' mode...")

for source_file_path in Path(packinfo["source_dir"]).glob("*/**/*_e.png"):
    
    export_file_path = PWE.Convertor.Utils.path_relative(
        source_file_path, packinfo["source_dir"], Path("./.packwrapper/export", Path(packinfo["source_dir"]).name)
    )
    
    _init.convert_to_P(source_file_path, export_file_path)

rp.package()