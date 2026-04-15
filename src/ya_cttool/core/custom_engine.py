from angr.engines import SimEngineFailure, SimEngineSyscall, HooksMixin, HeavyVEXMixin
from angr.engines.vex import HeavyResilienceMixin, SimInspectMixin, TrackActionsMixin


class CustomEngine( # type: ignore
    SimEngineFailure,
    SimEngineSyscall,
    HooksMixin,
    TrackActionsMixin,
    SimInspectMixin,
    HeavyResilienceMixin,
    HeavyVEXMixin,
    ):
    """
    """