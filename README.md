# kk.krun Collection

Ansible collection for deploying and running krun scripts on remote hosts.

## 安装

本地构建并安装：
```bash
ansible-galaxy collection build
ansible-galaxy collection install kk-krun-0.1.0.tar.gz
```

## 用法示例

```yaml
- name: Run krun to install docker
  hosts: all
  gather_facts: false
  tasks:
    - name: Run krun
      kk.krun.krun:
        name: "install-docker.sh"
        script_args:
          - "--force"
      register: krun_result

    - debug:
        var: krun_result
```

## 目录结构
- plugins/modules/krun.py  # 主模块
- tests/                  # 测试用例
- docs/                   # 文档