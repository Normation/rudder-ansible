# Rudder Ansible Collection

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

You can find more information and examples of use [here](https://github.com/Normation/rudder-ansible/blob/master/USAGE.md).

## Getting started

### Installation
To install the collection directly from this git repository, you must create a *requirements.yml* file and add the following content:
```yml
collections:
  - name: https://github.com/Normation/rudder-ansible.git
    type: git
    version: devel
```
Then execute the following command:
```bash
ansible-galaxy install -r requirements.yml
```
