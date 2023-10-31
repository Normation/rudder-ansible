# rudder_repository

This role configures the Rudder repositories, it is included as dependencies in each of
the roles listed above.

#### Role variables

- `rudder_version`: Rudder version(default: `8.0`)
- `repository`: Rudder repository domain (default: `repository.rudder.io`)
- `repository_url`: Complete Rudder repository URL (default: `empty`), used only when not empty, replace the server_version and rudder_repository when used.
- `repository_username`: Optional username to pass to repository if using credentials
- `repository_password`: Optional password to pass to repository if using credentials
- `rudder_update_cache`: Refresh the package manager cache or not (default: `yes`)
- `rudder_apt_key_url`: Repository key for APT based repositories (`false` if empty)
- `rudder_rpm_key_url`: Repository key for RPM based repositories (`false` if empty)

#### Example Playbook

```yaml
- name: Install Rudder Server
  hosts: server
  become: yes
  collections:
    - rudder.rudder
      roles:
        - role: rudder.rudder.rudder_repository
          vars:
            rudder_version: 8.0
            repository: "download.rudder.io"
            repository_username: "my_user"
            repository_password: "my_password"
```
