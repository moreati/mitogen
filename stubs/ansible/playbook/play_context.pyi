from typing import *

from ansible.playbook.base import Base
from ansible.playbook.play import Play


class PlayContext(Base):

    '''
    This class is used to consolidate the connection information for
    hosts in a play and child tasks, where the task may override some
    connection/authentication information.
    '''

    # connection fields, some are inherited from Base:
    # (connection, port, remote_user, environment, no_log)
    _docker_extra_args  = ... # type: str
    _remote_addr      = ... # type: str
    _password         = ... # type: str
    _private_key_file = ... # type: str
    _timeout          = ... # type: int
    _shell            = ... # type: str
    _network_os       = ... # type: str
    _connection_user  = ... # type: str
    _ssh_args         = ... # type: str
    _ssh_common_args  = ... # type: str
    _sftp_extra_args  = ... # type: str
    _scp_extra_args   = ... # type: str
    _ssh_extra_args   = ... # type: str
    _ssh_executable   = ... # type: str
    _ssh_transfer_method = ... # type: str
    _connection_lockfd= ... # type: int
    _pipelining       = ... # type: bool
    _accelerate       = ... # type: bool
    _accelerate_ipv6  = ... # type: bool
    _accelerate_port  = ... # type: int
    _executable       = ... # type: str
    _module_compression = ... # type: str

    # privilege escalation fields
    _become           = ... # type: bool
    _become_method    = ... # type: str
    _become_user      = ... # type: str
    _become_pass      = ... # type: str
    _become_exe       = ... # type: str
    _become_flags     = ... # type: str
    _prompt           = ... # type: str

    # backwards compatibility fields for sudo/su
    _sudo_exe         = ... # type: str
    _sudo_flags       = ... # type: str
    _sudo_pass        = ... # type: str
    _su_exe           = ... # type: str
    _su_flags         = ... # type: str
    _su_pass          = ... # type: str

    # general flags
    _verbosity        = ... # type: int
    _only_tags        = ... # type: set
    _skip_tags        = ... # type: set
    _check_mode       = ... # type: bool
    _force_handlers   = ... # type: bool
    _start_at_task    = ... # type: str
    _step             = ... # type: bool
    _diff             = ... # type: bool

    # Fact gathering settings
    _gather_subset    = ... # type: str
    _gather_timeout   = ... # type: str
    _fact_path        = ... # type: str

    password = ... # type: str
    become_pass = ... # type: str
    prompt = ... # type: str
    success_key = ... # type: str
    connection_lockfd = ... # type: Optional[int]

    def __init__(self, play: Optional[Play] = ..., options: Optional[Any] = ..., passwords: Optional[Dict[str, str]] = ..., connection_lockfd:Optional[int] = ...) -> None: ...

    accelerate = ... # type: bool
    accelerate_ipv6 = ... # type: bool
    accelerate_port = ... # type: int
    connection = ... # type: bool
    remote_user = ... # type: str
    port = ... # type: int
    become = ... # type: bool
    become_method = ... # type: str
    become_user = ... # type: str
    force_handlers = ... # type: bool

    def set_play(self, play: Play) -> None: ...

    check_mode = ... # type: bool
    ssh_common_args = ... # type: str
    docker_extra_args = ... # type: str
    sftp_extra_args = ... # type: str
    scp_extra_args = ... # type: str
    ssh_extra_args = ... # type: str
    private_key_file = ... # type: bool
    verbosity = ... # type: bool
    step = ... # type: bool
    start_at_task = ... # type: bool
    diff = ... # type: bool
    timeout = ... # type: int
    only_tags= ... # type: set
    skip_tags= ... # type: set

    def set_options(self, options: Any) -> None: ...
    def set_task_and_variable_override(self, task: Any, variables: Any, templar: Any) -> Base: ...
    def make_become_cmd(self, cmd: str, executable: Optional[str] = ...) -> str: ...
    def update_vars(self, variables: Mapping) -> None: ...
    def _get_attr_connection(self) -> str: ...
