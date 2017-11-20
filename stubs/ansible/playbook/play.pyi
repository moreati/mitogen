from typing import *

from ansible.playbook.base import Base
from ansible.playbook.become import Become
from ansible.playbook.taggable import Taggable

class Play(Base, Taggable, Become):
    _accelerate          = ... # type: bool
    _accelerate_ipv6     = ... # type: bool
    _accelerate_port     = ... # type: int
    _fact_path           = ... # type: str
    _gather_facts        = ... # type: bool
    _gather_subset       = ... # type: Optional[list]
    _gather_timeout      = ... # type: int
    _hosts               = ... # type: list
    _name                = ... # type: str
    _vars_files          = ... # type: list
    _vars_prompt         = ... # type: list
    _vault_password      = ... # type: str
    _roles               = ... # type: list
    _handlers            = ... # type: list
    _pre_tasks           = ... # type: list
    _post_tasks          = ... # type: list
    _tasks               = ... # type: list
    _force_handlers      = ... # type: bool
    _max_fail_percentage = ... # typr: float
    _serial              = ... # type: list
    _strategy            = ... # type: str

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def get_name(self) -> str: ...
    @staticmethod
    def load(data: dict, variable_manager: Optional[Any] = ..., loader: Optional[Any] = ...) -> Play: ...
    def process_data(self, ds: dict) -> Any: ...
    def _load_tasks(self, attr: Any, ds: Any) -> Any: ...
    def _load_pre_tasks(self, attr: Any, ds: Any) -> Any: ...
    def _load_post_tasks(self, attr: Any, ds: Any) -> Any: ...
    def _load_handlers(self, attr: Any, ds: Any) -> Any: ...
    def _load_roles(self, attr: Any, ds: Any) -> Any: ...
    def _load_vars_prompt(self, attr: Any, ds: Any) -> List[Dict]: ...
