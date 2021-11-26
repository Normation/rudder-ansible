# Ansible Collection - rudder

A set of [Ansible][ansible] roles for installing and managing [Rudder][rudder] servers and agents. The roles works with
Debian, RedHat and SUSE based systems.

- `rudder_agent`: Configures repository and installs a Rudder agent
- `rudder_relay`: Configures repository and installs a Rudder relay
- `rudder_server`: Configures repository and installs a Rudder server
- `rudder_repository`: Configures Rudder repositories


[ansible]: http://www.ansible.com/
[rudder]: http://www.rudder.io/

rudder_agent
------------

### Role variables: ###

This role does not auto accept the node. It only configures the repository
and installs the packages.

- `policy_server`: Rudder policy server (default: `rudder.server`)
- `agent_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

### Example Playbook: ###
```yaml
- name: Install Rudder agents
  hosts: agents
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_agent
          vars:
            agent_version: 6.2

```

rudder_server
------------

### Role variables: ###

- `server_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

### Example Playbook: ###
```yaml
- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_server
          vars:
            server_version: 6.2
```

rudder_relay
------------

This role does not auto accept the node nor promotes it to relay. It only configures the repository
and installs the packages.

### Role variables: ###

- `relay_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

### Example Playbook: ###
```yaml
- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_relay
          vars:
            relay_version: 6.2
```

rudder_repository
------------

This role configures the Rudder repositories, it is included as dependencies in each of
the roles listed above.

### Role variables: ###

- `rudder_version`: Rudder version(default: `6.2`)
- `repository`: Rudder repository domain (default: `repository.rudder.io`)
- `repository_username`: Optional username to pass to repository if using credentials
- `repository_password`: Optional password to pass to repository if using credentials
- `update_cache`: Refresh the package manager cache or not (default: `yes`)
- `rudder_apt_key_url`: Repository key for APT based repositories
- `rudder_rpm_key_url`: Repository key for RPM based repositories

### Example Playbook: ###
```yaml
- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_repository
          vars:
            rudder_version: 6.2.10
            repository: "download.rudder.io"
            repository_username: "my_user"
            repository_password: "my_password"
```
