import os

import cpuinfo
import torch
import yaml

from app.classes.Collection import Collection
from app.classes.CustomLogger import logger
from app.classes.Model import Model, Result
from app.constants import paths
from app.constants.types import LogLevel


class Device:
    def __init__(self, name="CPU", inference_string="cpu", cudaDevice=None):
        self.name = name
        self.inference_string = inference_string
        self.cudaDevice = cudaDevice


class ModelHandler:
    def __init__(self):
        self.collections = []
        self.models = []
        self.collections_filtered = []
        self.models_filtered = []
        self.getMMDetModels()
        self.devices = []
        self.usrCheckpoints = []
        self.usrConfigs = []

        self.get_UserModels()
        self.init_deviceOptions()

    def getMMDetModels(self):
        logger.log(
            "Scanning Directory %s for collections and models ... "
            % (paths.MMDET_MODELS),
            LogLevel.DEBUG,
            None,
        )
        for dir in os.scandir(paths.MMDET_MODELS):
            if dir.is_dir():
                for file in os.scandir(dir.path):
                    if file.is_file():
                        ext = os.path.splitext(file.path)[-1].lower()
                        coll = dir.name
                        if ext == ".yml":
                            self.parse_yml_file(file.path, coll)

    def get_UserModels(self):
        self.usrCheckpoints.clear()
        self.usrCheckpoints.clear()
        logger.log(
            "Scanning Directory %s for and Configs & Weights ... "
            % (paths.USER_MODELS),
            LogLevel.DEBUG,
            None,
        )
        for dir in os.scandir(paths.USER_MODELS):
            if dir.is_dir() and dir.name == "checkpoints":
                for file in os.scandir(dir.path):
                    if file.is_file():
                        self.usrCheckpoints.append(file.name)
            elif dir.is_dir() and dir.name == "configs":
                for file in os.scandir(dir.path):
                    if file.is_file():
                        self.usrConfigs.append(file.name)

    def parse_yml_file(self, ymlFile, dir):
        with open(ymlFile) as f:
            json_data = yaml.safe_load(f)
            if "Collections" in json_data:
                self.collections.append(self.parse_collection(json_data, dir))

    def parse_collection(self, dict, dir):
        coll = None
        collection_json = dict.get("Collections")[0]
        if "Name" in collection_json:
            coll = Collection(
                collection_json.get("Name"),
                collection_json.get("Metadata"),
                collection_json.get("Paper"),
                collection_json.get("README"),
                collection_json.get("Code"),
            )
        else:
            coll = Collection(name=dir)

        # Create ModelInfo objects for each model in the collection
        if dict.get("Models"):
            for model_data in dict.get("Models"):
                model = Model(
                    model_data.get("Name"),
                    model_data.get("In Collection"),
                    model_data.get("Config"),
                    model_data.get("Metadata"),
                    model_data.get("Weights"),
                )
                for r in model_data.get("Results"):
                    result = Result(r.get("Task"), r.get("Dataset"), r.get("Metrics"))
                    model.add_results(result)
                coll.add_model(model)
                self.models.append(model)
        return coll

    def find_collection(self, name):
        for c in self.collections:
            if c.name == name:
                return c

        return None

    def find_model(self, name):
        for m in self.models:
            if m.name == name:
                return m
        return None

    def init_deviceOptions(self):
        # get CPU device
        device = Device(cpuinfo.get_cpu_info()["brand_raw"], "cpu")
        self.devices.append(device)  # get only the brand name

        # get Cudadevices
        for i in range(torch.cuda.device_count()):
            inference_str = "cuda:" + str(i)
            logger.log(
                "Cuda device found:" + torch.cuda.get_device_properties(i).name,
                log_level=LogLevel.DEBUG,
            )
            device = Device(
                torch.cuda.get_device_properties(i).name,
                inference_str,
                torch.cuda.device(i),
            )
            self.devices.append(device)
