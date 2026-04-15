from dataclasses import dataclass
import os
from pathlib import Path
from typing import cast
from typing_extensions import Self

from marshmallow import Schema, fields, post_load, ValidationError
import yaml

from ya_cttool import TargetConfig, TargetConfigSchema

@dataclass
class TestConfig:
    cases_bin_dir: str
    cases_expected_dir: str
    cases_src_dir: str
    results_dir: str
    cases_bin: list[str]
    compiler_info_file: str
    compiler: str
    fail: bool
    test_mode: bool
    save_explored_states: bool

class TestConfigSchema(Schema):
    cases_bin_dir = fields.String(required=True)
    cases_src_dir = fields.String(required=True)
    cases_expected_dir = fields.String(required=True)
    results_dir = fields.String(required=True)
    cases_bin = fields.List(fields.String, required=True)
    compiler_info_file = fields.String(required=True)
    compiler = fields.String(required=True)
    fail = fields.Boolean(required=True)
    test_mode = fields.Boolean(required=True)
    save_explored_states  = fields.Boolean(required=True)

    @post_load
    def make_test_config(self, data, **kwargs) -> TestConfig:
        return TestConfig(**data)


class ConfigManager:
    _instance: Self | None = None
    _test_config: TestConfig | None = None
    _target_config: TargetConfig | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def load_configs(self, path: str | Path = 'config/test.yml') -> Self:
        if not os.path.isfile(path):
            raise FileNotFoundError("Missing test configuration file.")

        with open(path) as f:
            raw = yaml.safe_load(f)

        if raw.get('test_config') is None:
            raise ValueError('Test configuration must contain a `test_config` key.')
        
        if raw.get('app_config') is None:
            raise ValueError('Test configuration must contain a `app_config` key.')
        
        try:
            self._test_config = cast(TestConfig, TestConfigSchema().load(raw['test_config']))
        except ValidationError:
            raise

        try:
            self._target_config = cast(TargetConfig, TargetConfigSchema().load(raw['app_config']))
        except ValidationError:
            raise
        
        return self

    @property
    def test_config(self) -> TestConfig:
        if self._test_config is None:
            raise Exception("Configuration has not been loaded.")
        return self._test_config

    @property
    def target_config(self) -> TargetConfig:
        if self._target_config is None:
            raise Exception("Configuration has not been loaded.")
        return self._target_config

    def dump(self, path: str):
        if self._test_config is None:
            raise Exception("Configuration has not been loaded.")

        serialized = TestConfigSchema().dump(self._test_config)
        with open(os.path.join(path, "config-test.yml"), "w") as f:
            yaml.dump(serialized, f)

        serialized = TargetConfigSchema().dump(self._target_config)
        with open(os.path.join(path, "config-app.yml"), "w") as f:
            yaml.dump(serialized, f)
