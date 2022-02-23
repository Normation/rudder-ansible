# rudder_agent

#### Role variables

This role does not auto accept the node. It only configures the repository
and installs the packages.

- `policy_server`: Rudder policy server (default: `rudder.server`)
- `agent_version`: Rudder version(default: `7.0`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_url`: Complete Rudder repository URL (default: `empty`), used only when not empty, replace the server_version and rudder_repository when used.
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials
- `update_cache`: Refresh the package manager cache or not (default: `yes`)
- `apt_key_url`: Repository key for APT based repositories
- `rpm_key_url`: Repository key for RPM based repositories

#### Example Playbook

```yaml
- name: Install Rudder agents
  hosts: agents
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_agent
          vars:
            agent_version: 7.0
```
