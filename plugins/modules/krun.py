#!/usr/bin/python
# Copyright (c) 2025 kk
# MIT License: https://opensource.org/licenses/MIT

DOCUMENTATION = r'''
---
module: krun
short_description: Run krun scripts on remote hosts
version_added: "1.0.0"
description:
  - 自动在远程主机安装 krun 并运行指定脚本。
options:
  name:
    description:
      - krun 要执行的脚本名（如 install-docker.sh）。
    required: true
    type: str
  script_args:
    description:
      - 传递给 krun 脚本的额外参数（列表）。
    required: false
    type: list
    elements: str
check_mode:
  description:
    - 支持 check_mode，check_mode 下不会实际执行 krun，仅返回将要执行的命令。
  type: bool
  default: false
author:
  - kk (@kevin197011)
'''

EXAMPLES = r'''
- name: Krun install package
  kk.krun.krun:
    name: "install-docker.sh"
    script_args:
      - "--force"
      - "--debug"
'''

RETURN = r'''
stdout:
  description: krun 命令的标准输出
  type: str
  returned: always
stderr:
  description: krun 命令的标准错误
  type: str
  returned: always
rc:
  description: krun 命令的返回码
  type: int
  returned: always
changed:
  description: 是否有变更
  type: bool
  returned: always
would_run:
  description: check_mode 下返回，将要执行的命令
  type: str
  returned: when check_mode
msg:
  description: 任务执行摘要，包含 stdout、stderr、rc
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import os

def ensure_krun(module):
    krun_path = os.path.expanduser("~/.krun/bin/krun")
    if not os.path.exists(krun_path):
        install_cmd = (
            "curl -fsSL -o /tmp/krun https://raw.githubusercontent.com/kevin197011/krun/main/bin/krun && "
            "mkdir -p ~/.krun/bin && "
            "mv /tmp/krun ~/.krun/bin/krun && "
            "chmod +x ~/.krun/bin/krun"
        )
        rc = subprocess.call(install_cmd, shell=True)
        if rc != 0:
            module.fail_json(msg="Failed to install krun")

def run_krun(module, name, script_args=None):
    krun_path = os.path.expanduser("~/.krun/bin/krun")
    cmd = [krun_path, name]
    if script_args:
        cmd.extend(script_args)
    rc = 0
    out = ""
    err = ""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = result.stdout
        err = result.stderr
    except subprocess.CalledProcessError as e:
        rc = e.returncode
        out = e.stdout
        err = e.stderr
    return rc, out, err, cmd

def main():
    module_args = dict(
        name=dict(type='str', required=True),
        script_args=dict(type='list', elements='str', required=False, default=[])
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    name = module.params['name']
    script_args = module.params['script_args']

    krun_path = os.path.expanduser("~/.krun/bin/krun")
    cmd = [krun_path, name] + (script_args or [])

    if module.check_mode:
        module.exit_json(changed=False, would_run=' '.join(cmd), msg=f"[CHECK_MODE] Would run: {' '.join(cmd)}")

    ensure_krun(module)
    rc, out, err, _ = run_krun(module, name, script_args)

    msg = f"krun return code: {rc}\nstdout:\n{out}\nstderr:\n{err}"

    if rc != 0:
        module.fail_json(msg=msg, stdout=out, stderr=err, rc=rc)
    else:
        module.exit_json(changed=True, stdout=out, stderr=err, rc=rc, msg=msg)

if __name__ == '__main__':
    main()