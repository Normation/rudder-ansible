# rudder_server

#### Role variables

- `server_version`: Rudder version(default: `7.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_url`: Complete Rudder repository URL (default: `empty`), used only when not empty, replace the server_version and rudder_repository when used.
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials
- `update_cache`: Refresh the package manager cache or not (default: `yes`)
- `apt_key_url`: Repository key for APT based repositories
- `rpm_key_url`: Repository key for RPM based repositories

#### Example Playbook

```yaml
- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_server
          vars:
            server_version: 7.0
```

#### Example playbook: server and agents connect to that server

From: https://github.com/safespring-community/terraform-modules/tree/main/examples/v2-rudder-minimal-poc
```yaml

- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  tasks:
    - import_role:
        name: rudder.rudder.rudder_server
      vars:
        server_version: 7.0

- name: Install Rudder agents
  hosts: agents_host_group
  become: yes
  collections:
    - rudder.rudder
  tasks:
    - import_role:
        name: rudder.rudder.rudder_agent
      vars:
        agent_version: 7.0
        policy_server: "{{hostvars['hostname_of_server']['ansible_default_ipv4']['address']}}"

```
