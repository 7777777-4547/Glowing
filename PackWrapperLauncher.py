import PackWrapperDownloader as PWD

PWD.main(version="v0.0.2-alpha")
print("[Launcher] Launching PackWrapper...")

import PackWrapper as PW
from PackWrapper import ScriptSystem

PW.init()

pack_info = PW.get_packinfo()

ScriptSystem.init("version_script", PW.get_properties_main())
ScriptSystem.run_script("of_1.21.2")
ScriptSystem.run_script("of_1.20")
ScriptSystem.run_script("of_1.19")
ScriptSystem.run_script("of_1.16")
ScriptSystem.run_script("of_1.14")
ScriptSystem.run_script("of_1.13")
ScriptSystem.run_script("of_1.12")
ScriptSystem.run_script("of_1.9")