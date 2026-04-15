from dataclasses import dataclass
from enum import Enum
import os
from typing_extensions import Self, cast

from confz import BaseConfig, FileSource
from marshmallow import Schema, fields, post_load, ValidationError
import yaml
from pydantic import Field, field_validator

class LogLevel(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class LoggingConfig(BaseConfig):
    file_level: LogLevel
    stream_level: LogLevel

    @field_validator("file_level", "stream_level", mode="before")
    @classmethod
    def _coerce_level(cls, v):
        if v in ("", None):
            return None
        if isinstance(v, str):
            name = v.strip().upper()
            try:
                return LogLevel[name]
            except KeyError:
                raise ValueError(f"Invalid log level: {v!r}")
        raise ValueError(f"Invalid log level type: {type(v).__name__}")


class OutputsConfig(BaseConfig):
    dir: str
    save_explored_states: bool
    save_results: bool
    save_metadata: bool

class CommonConfig(BaseConfig):
    outputs: OutputsConfig
    logging: LoggingConfig
    progress_bars_disabled: bool = Field(default=False)
    timeout: int = Field(default=600)

    CONFIG_SOURCES = FileSource("config/common.yaml")

@dataclass
class TargetConfig:
    min_consolidation_threshold: int
    max_consolidation_threshold: int
    source_code_dirs: list[str]
    hooks: dict


class TargetConfigSchema(Schema):
    min_consolidation_threshold = fields.Integer()
    max_consolidation_threshold = fields.Integer()
    source_code_dirs = fields.List(fields.String)
    basic_block_consolidation_threshold = fields.Integer()
    hooks = fields.Dict()

    @post_load
    def make_test_config(self, data, **kwargs) -> TargetConfig:
        try:
            config = TargetConfig(**data)
        except TypeError as exc:
            raise ValidationError(f"{exc}")
        return config


class TargetConfigManager:
    _instance: Self | None = None
    _config: TargetConfig | None = None
    config_default_path = "config/app.yml"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TargetConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self, *, config: TargetConfig | None = None, path: str | None = None
    ) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        if config is None:
            if path is None:
                path = self.config_default_path
            with open(path) as f:
                raw = yaml.safe_load(f)
            try:
                self._config = cast(TargetConfig, TargetConfigSchema().load(raw))
            except ValidationError:
                raise
        elif path is None and config is not None:
            self._config = config
        else:
            raise ValueError("`path` OR `config` must be defined, OR `path` AND `config` must be undefined")
        self._initialized = True

    def get_config(self) -> TargetConfig:
        if self._config is None:
            raise Exception("Configuration has not been loaded.")
        return self._config

    def dump(self, path: str):
        if self._config is None:
            raise Exception("Configuration has not been loaded.")
        serialized = TargetConfigSchema().dump(self._config)
        with open(os.path.join(path, "config-app.yml"), "w") as f:
            yaml.dump(serialized, f)
