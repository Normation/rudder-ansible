# Rudder Ansible Collection

<!-- TABLE OF CONTENTS -->
<summary>Table of Contents</summary>
<ol>
  <li>
    <a href="#overview">Overview</a>
  </li>
  <li>
    <a href="#getting-started">Getting Started</a>
    <ul>
      <li>
        <a href="#installation">Installation</a>
        <ul>
        <li>
          <a href="#with-ansible-210">With Ansible >= 2.10</a>
        </li>
        <li>
          <a href="#with-ansible-210">With Ansible < 2.9</a>
        </li>
        </ul>
      </li>
    </ul>
  </li>
  <li><a href="#role-usage">Role usage</a>
    <ul>
      <li>
        <a href="#rudder_agent">Deploy Rudder agent role</a>
          <ul>
          <li><a href="#role-variables">Role variables</a></li>
          <li><a href="#example-playbook">Example Playbook</a></li>
        </ul>
      </li>
    </ul>
    <ul>
      <li>
        <a href="#rudder_server">Deploy Rudder root server role</a>
          <ul>
          <li><a href="#role-variables">Role variables</a></li>
          <li><a href="#example-playbook">Example Playbook</a></li>
        </ul>
      </li>
    </ul>
    <ul>
      <li>
        <a href="#rudder_relay">Deploy Rudder relay server role</a>
          <ul>
          <li><a href="#role-variables">Role variables</a></li>
          <li><a href="#example-playbook">Example Playbook</a></li>
        </ul>
      </li>
    </ul>
    <ul>
      <li>
        <a href="#rudder_repository">Manage Rudder repository role</a>
          <ul>
          <li><a href="#role-variables">Role variables</a></li>
        </ul>
      </li>
    </ul>
  </li>
    <li><a href="#module-usage">Module usage</a>
    <ul>
      <li>
        <a href="#node_settings">node_settings</a>
          <ul>
          <li><a href="#module-parameters">Module parameters</a></li>
          <li><a href="#example-playbook">Example Playbook</a></li>
        </ul>
      </li>
    </ul>
        <ul>
      <li>
        <a href="#server_settings">server_settings</a>
          <ul>
          <li><a href="#module-parameters">Module parameters</a></li>
          <li><a href="#example-playbook">Example Playbook</a></li>
        </ul>
      </li>
    </ul>
      <li>
    <a href="#going-further">Going further</a>
    <ul>
      <li><a href="#uninstall-the-collection">Uninstall the collection</a></li>
    </ul>
  </li>
  <li>
    <a href="#development">Development</a>
    <ul>
      <li><a href="#run-checks-locally-with-docker">Run checks locally with Docker</a></li>
    </ul>
        <ul>
      <li><a href="#push-this-collection-on-ansible-galaxy">Push this collection on Ansible Galaxy</a></li>
    </ul>
  </li>
</ol>

## Overview
This Ansible collection allows to manage and interact with one or more Rudder instances.
It was created in order to gather all the necessary tools for a good integration of Ansible with Rudder.

This collection allows you to:

* Provides a plugin that extracts the inventory from Rudder and transforms it into Ansible format so that it can be retrieved (in CLI, in Ansible Tower/AWX).
* Module for provisioning the configuration of Rudder nodes.
* Module to configure the different parameters of a Root Rudder server.
* An armada of roles that allow each to deploy a particular element:
  - _rudder_agent_ as the name suggests, allows you to deploy and configure a Rudder agent.
  - _rudder_server_ allows you to deploy, provision and configure the nodes properties of a root server.
  - _rudder_relay_ allows you to deploy a relay server and configure it.
  - _rudder_repository_ allows the management of private Rudder repos.

## Getting started

### Installation

#### With Ansible >= 2.10
To install the collection directly from this git repository, you must create a *requirements.yml* file and add the following content:

```yml
collections:
  - name: https://github.com/Normation/rudder-ansible.git
    type: git
    version: master
```

Then execute the following command:

```bash
ansible-galaxy install -r requirements.yml
```

#### With Ansible < 2.9

You must first clone the current git repo, move to the directory of the cloned repo and then use the following command:

```bash
ansible-galaxy collection install .
```

## Role usage

A set of [Ansible][ansible] roles for installing and managing [Rudder][rudder] servers and agents. The roles works with
**Debian**, **RedHat** and **SUSE** based systems.

- `rudder_agent`: Configures repository and installs a Rudder agent
- `rudder_relay`: Configures repository and installs a Rudder relay
- `rudder_server`: Configures repository and installs a Rudder server
- `rudder_repository`: Configures Rudder repositories


[ansible]: http://www.ansible.com/
[rudder]: http://www.rudder.io/

### rudder_agent

#### Role variables

This role does not auto accept the node. It only configures the repository
and installs the packages.

- `policy_server`: Rudder policy server (default: `rudder.server`)
- `agent_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

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
            agent_version: 6.2
```

### rudder_server

#### Role variables

- `server_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

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
            server_version: 6.2
```

### rudder_relay

This role does not auto accept the node nor promotes it to relay. It only configures the repository
and installs the packages.

#### Role variables

- `relay_version`: Rudder version(default: `6.2`)
- `rudder_repository`: Rudder repository domain (default: `repository.rudder.io`)
- `rudder_repository_username`: Optional username to pass to repository if using credentials
- `rudder_repository_password`: Optional password to pass to repository if using credentials

#### Example Playbook

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

### rudder_repository

This role configures the Rudder repositories, it is included as dependencies in each of
the roles listed above.

#### Role variables

- `rudder_version`: Rudder version(default: `6.2`)
- `repository`: Rudder repository domain (default: `repository.rudder.io`)
- `repository_username`: Optional username to pass to repository if using credentials
- `repository_password`: Optional password to pass to repository if using credentials
- `update_cache`: Refresh the package manager cache or not (default: `yes`)
- `rudder_apt_key_url`: Repository key for APT based repositories
- `rudder_rpm_key_url`: Repository key for RPM based repositories

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
            rudder_version: 6.2.10
            repository: "download.rudder.io"
            repository_username: "my_user"
            repository_password: "my_password"
```
## Module usage
The collection provides 2 major roles allowing to configure a Rudder root server but also to set up nodes dynamically (adding node properties for example).


### node_settings

Configure Rudder nodes parameters via APIs.
#### Module parameters

- `rudder_url` (str): Providing Rudder server IP address. Defaults to `localhost`.
- `rudder_token` (str): Providing Rudder server token. Defaults to the content of /var/rudder/run/api-token if not set.
- `validate_certs` (bool): Choosing either to ignore or not Rudder certificate validation. Defaults to `true`.
- `node_id` (str): Define the identifier of the node to be configured.
- `policy_mode` (str): Set the policy mode
  - *Choices*: `audit`, `enforce`, `default`, `keep`
- `pending` (str): Set the status of the (pending) node
  - *Choices*: `accepted` or `refused`
- `state` (str): Set the node life cycle state
  - *Choices*: `enabled`, `ignored`, `empty-policies`, `initializing`, `preparing-eol`
- `properties` (list): Define a list of properties
  - *Subparameters*:
    - `name` (str): Property name
    - `value` (str): Property value
- `agent_key` (dict): Define information about agent key or certificate
  - *Subparameters*:
    - `status` (str): TODO
      - *Choices*: `certified`, `undefined`
    - `value` (str): Agent key, PEM format
- `include` (str): Level of information to include from the node inventory.
- `query` (dict): The criterion you want to find for your nodes.
  - *Subparameters*:
    - `composition` (str): Boolean operator to use between each where criteria.
      - *Choices*: `or`, `and`
    - `select` (str): What kind of data we want to include. Here we can get policy servers/relay by setting *nodeAndPolicyServer*. Only used if where is defined.
    - `where` (list): The criterion you want to find for your nodes. List of selectors.
      - *Subparameters*:
        - `object_type` (str): Object type from which the attribute will be taken.
        - `attribute` (str): Attribute to compare to value.
        - `comparator` (str): Comparator type to use.
          - *Choices*: `or`, `and`
        - `value` (str): Value to compare to.
#### Example playbook

```yaml
# Example 1
- name: Simple Modify Rudder Node Settings
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      node_id: my_node_id
      policy_mode: enforce

# Example 2
- name: Complex Modify Rudder Node Settings
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      node_id: root
      pending: accepted
      policy_mode: audit
      state: enabled
      properties:
        name: "env_type"
        value: "production"
      validate_certs: False

# Example 3
- name: Complex Modify Rudder Node Settings with query
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  node_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      pending: accepted
      policy_mode: audit
      state: enabled
      properties:
        name: "env_type"
        value: "production"
      query:
        select: "nodeAndPolicyServer"
        composition: "and"
        where:
          - object_type: "node"
            attribute: "nodeHostname"
            comparator: "regex"
            value: "rudder-ansible-node.*"
```

### server_settings
Configure Rudder Server parameters via APIs.
#### Module parameters
- `rudder_url` (str): Providing Rudder server IP address. Defaults to `localhost`.
- `rudder_token` (str): Providing Rudder server token. Defaults to the content of /var/rudder/run/api-token if not set.
- `name` (str): The name of the parameter to set.
- `value` (str): The value defined to modify a given parameter name.
- `validate_certs` (bool): Choosing either to ignore or not Rudder certificate validation. Defaults to `true`.

#### Example playbook

```yaml
# Example 1
- name: Simple Modify Rudder Settings
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  server_settings:
      name: "modified_file_ttl"
      value: "23"

# Example 2
- name: Complex Modify Rudder Settings
  hosts: server
  become: yes
  collections:
    - rudder.rudder
  server_settings:
      rudder_url: "https://my.rudder.server/rudder"
      rudder_token: "<rudder_server_token>"
      name: "modified_file_ttl"
      value: "22"
      validate_certs: False
```

## Going further

### Uninstall the collection

To delete the collection, if you have not changed the default settings, is stored in `~/.ansible/collections/ansible_collections/`. So you will have to delete the directory named "*rudder*".

You can use the following command to see if the collection is correctly installed and to see where it is installed.

```bash
ansible-galaxy collection list
```

## Development

### Run checks locally with [Docker](https://www.docker.com/)
You have the possibility to run status checks on the code before publishing it locally. To do this, you need to create a Dockerfile (with `ansible-test.Dockerfile` for example) with the content below in the *root of the project*.

```dockerfile
FROM debian:bullseye
ARG USER_ID=1000
COPY ci/user.sh .
RUN ./user.sh $USER_ID

RUN apt-get -y update && \
    apt-get install -y ansible git python3-pip
RUN pip install pycodestyle voluptuous yamllint

RUN mkdir -p /tmp/ansible_collections/rudder/rudder

COPY . /tmp/ansible_collections/rudder/rudder/
WORKDIR "/tmp/ansible_collections/rudder/rudder/"

ENTRYPOINT ["/bin/bash", "-c"]
```

To build the container :

```bash
docker build . -f ansible-test.Dockerfile
```

To start the verification, simply use the command :

```bash
docker run <container-hash> "ansible-test sanity" 
```
If you make new changes in the code, you will have to restart a build of the container and make a new run of the Docker command that goes well with the new container hash obtained.

### Push this collection on Ansible Galaxy

To push the collection, you must have a [GitHub](https://github.com/) account.

* Log in to Galaxy with the account that will perform the buid and publication. 
* Generate Galaxy API key, more informations [here](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html#synopsis).
* Modify the content of the `galaxy.yml` file before publishing.
* Build the collection locally with `ansible-galaxy collection build`.
* Then *publish* the collection with the following command `ansible-galaxy collection publish ./rudder-ansible-1.0.0.tar.gz --api-key you_galaxy_api_key`

