import json
from io import TextIOWrapper, UnsupportedOperation
from json import JSONDecodeError
import os

class Config:
    def __init__(self, log):
        self.log = log

        if not os.path.exists("config.json"):
            self.log("config.json not found, creating new one")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)            

        try:
            with open("config.json", "r") as file:
                self.log("config opened")
                config = json.load(file)
                if config.get("cooldown") is None or config.get("keepPlayerFiles") is None or config.get("dumpDataToFiles") is None:
                    self.log("some config values are None, getting new config")
                    config = self.config_dialog(file)
                
        except (JSONDecodeError, UnsupportedOperation):
            self.log("invalid file")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
        finally:
            self.cooldown = config["cooldown"]
            self.dumpDataToFiles = config["dumpDataToFiles"]
            self.keepPlayerFiles = config["keepPlayerFiles"]
            self.log(f"got cooldown with value '{self.cooldown}'")

                

    def config_dialog(self, fileToWrite: TextIOWrapper):
        self.log("color config prompt called")
        jsonToWrite = {"cooldown": 1, "dumpDataToFiles": "false", "keepPlayerFiles": "false"}
        
        json.dump(jsonToWrite, fileToWrite)
        return jsonToWrite