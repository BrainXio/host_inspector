# Ansible Role: brainxio.host_inspector

This Ansible role provides a custom module for inspecting host systems, gathering various system information, and logging. It includes functionalities for checking CPU usage, memory status, disk information, network details, and system metadata.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Role Variables](#role-variables)
    - [Defaults](#defaults)
- [Dependencies](#dependencies)
- [Usage](#usage)
    - [Example Playbook](#example-playbook)
- [License](#license)
- [Author Information](#author-information)

## Installation

To install this role, you can use `ansible-galaxy`:

```sh
ansible-galaxy install brainxio.host_inspector
```

Or you can clone the repository directly:

```sh
git clone <repository_url> /path/to/your/roles/brainxio.host_inspector
```

## Requirements

- **Ansible**: >= 2.9
- **Python**: >= 3.5 on the controller node
- **Operating System**: This role has been tested on Linux distributions. It might require adjustments for other operating systems.

## Role Variables

### Defaults

The role uses the following default variables which can be overridden:

```yaml
logging_path: "logs"
data_path: "data"
```

- `logging_path`: Directory where logs will be stored.
- `data_path`: Directory where collected data might be written if needed.

## Dependencies

None explicitly, but it assumes that the system supports standard Unix commands for system inspection.

## Usage

This role includes tasks that will gather host information using a custom Ansible module `host_inspector`.

### Example Playbook

```yaml
---
- hosts: all
  roles:
    - role: brainxio.host_inspector
      logging_path: "/custom/path/to/logs"
```

## License

[The Unlicense](UNLICENSE)

## Author Information

This role was created by [BrainXio](https://github.com/BrainXio).

Feel free to contribute, report issues, or suggest enhancements via the GitHub repository.
