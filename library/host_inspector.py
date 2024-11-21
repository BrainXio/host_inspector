#!/usr/bin/python
"""Ansible module for host inspection with various utility functions."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import subprocess
import platform
import socket
import re
import logging
import datetime
import uuid
from ansible.module_utils.basic import AnsibleModule

# Setup logging
logger = logging.getLogger('host_inspector')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#---------------------------------------------------------------------------------------
# Message Handling
#---------------------------------------------------------------------------------------
class MessageHandler:
    """Class for handling and manipulating message content."""

    @staticmethod
    def hello_world():
        """Generate a greeting message.

        Returns:
            str: A greeting message with the primary keys of the result object.
        """
        user = os.environ.get('USER', 'World')
        greeting = f"Hello, {user}!"
        return greeting

    @staticmethod
    def format_message(base_msg, prepend='', append=''):
        """Format the message with prepend and append strings.

        Args:
            base_msg (str): The base message to format.
            prepend (str): String to prepend to the message.
            append (str): String to append to the message.

        Returns:
            str: Formatted message.
        """
        return f"{prepend}{base_msg}{append}"

#---------------------------------------------------------------------------------------
# Base Inspection Utilities
#---------------------------------------------------------------------------------------
class BaseInspection:
    """Base class for host inspection functionalities."""

    @staticmethod
    def get_environment_variables():
        """Retrieve and return all environment variables.

        Returns:
            dict: A dictionary containing all environment variables.
        """
        return {key: value for key, value in os.environ.items()}

    @staticmethod
    def _setup_logging(log_path=None):
        """Configure logging based on whether a custom log path is provided."""
        if log_path:
            log_filename = log_path
            if not os.path.exists(os.path.dirname(log_path)):
                os.makedirs(os.path.dirname(log_path))
        else:
            logs_dir = 'logs'
            if not os.path.isdir(logs_dir):
                os.makedirs(logs_dir)
            now = datetime.datetime.now()
            epoch = int(now.timestamp())
            log_filename = f"{logs_dir}/{epoch}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()  # This will keep the console output
            ]
        )
        return logging.getLogger(__name__)

    @staticmethod
    def _run_cmd(command, timeout=30, shell=True, check=True, text=True):
        """Run a shell command with error handling and timeout."""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    shell=shell, timeout=timeout, check=check, text=text)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logging.error(f"Command '{command}' timed out")
            return None
        except subprocess.CalledProcessError:
            logging.error(f"Command '{command}' failed")
            return None

    @staticmethod
    def _parse_cpu_info():
        """Parse /proc/cpuinfo to gather CPU information."""
        cpuinfo = {}
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = map(str.strip, line.split(':', 1))
                    cpuinfo[key] = value
        return cpuinfo

    @staticmethod
    def _define_limits():
        """Set up system limits data structure."""
        logging.info("Defining system limits")
        return {
            'cpu_load': 80,  # Percentage
            'memory_usage': 90,  # Percentage
            'disk_usage': 85   # Percentage
        }

    @staticmethod
    def execute():
        """Execute the host intel gathering action.

        Args:
            verbosity (int): The level of detail in the output.

        Returns:
            dict: Contains the message and any gathered data as separate keys.
        """
        cpu = {'count': None, 'model': None, 'load': None}
        disk = {'total': None, 'used': None, 'free': None, 'usage': None}
        memory = {'total': None, 'used': None, 'available': None, 'usage': None}
        network = {'hostname': socket.gethostname(), 'interfaces': {}}
        system = {
            'os': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine()
        }

        # CPU Information
        cpuinfo = BaseInspection._parse_cpu_info()
        cpu['count'] = int(cpuinfo.get('processor', 0)) + 1
        cpu['model'] = cpuinfo.get('model name')

        # CPU Load
        load_output = BaseInspection._run_cmd("uptime", shell=True)
        if load_output:
            load = re.search(r'load average: ([\d.]+)', load_output)
            if load:
                cpu['load'] = float(load.group(1))

        # Memory Information
        meminfo = BaseInspection._run_cmd("cat /proc/meminfo", shell=True)
        if meminfo:
            for line in meminfo.split('\n'):
                if line.startswith("MemTotal:"):
                    memory['total'] = int(line.split()[1]) * 1024
                elif line.startswith("MemAvailable:"):
                    memory['available'] = int(line.split()[1]) * 1024

        mem_used = BaseInspection._run_cmd("free -b | grep 'Mem:' | awk '{print $3}'", shell=True)
        if mem_used:
            memory['used'] = int(mem_used)
            memory['usage'] = (memory['used'] / memory['total']) * 100 if memory['total'] else 0

        # Disk Information
        disk_output = BaseInspection._run_cmd("df -B 1 /", shell=True)
        if disk_output:
            for line in disk_output.split('\n'):
                if '/dev/' in line:
                    parts = line.split()
                    disk['total'] = int(parts[1])
                    disk['used'] = int(parts[2])
                    disk['free'] = int(parts[3])
                    disk['usage'] = int(parts[4].rstrip('%'))

        # Network Information
        ip_output = BaseInspection._run_cmd("ip -o addr show", shell=True)
        if ip_output:
            for iface in ip_output.split('\n'):
                if not iface.strip():
                    continue
                parts = iface.split()
                interface = parts[1]
                if interface not in network['interfaces']:
                    network['interfaces'][interface] = []
                addr_info = parts[-1].split('/')
                if len(addr_info) > 1:
                    network['interfaces'][interface].append({
                        'address': addr_info[0],
                        'netmask': addr_info[1] if len(addr_info) > 1 else None
                    })

        # Prepare the response
        msg = "System intelligence gathered."
        
        return {
            'msg': msg,
            'cpu': cpu, 
            'memory': memory, 
            'disk': disk, 
            'network': network, 
            'system': system, 
            'limits': BaseInspection._define_limits()
        }

#---------------------------------------------------------------------------------------
# Metadata Handling
#---------------------------------------------------------------------------------------
class MetaData:
    """Class responsible for managing host_inspector's metadata."""

    @staticmethod
    def get_metadata():
        """Collect and return metadata about the host and the Python environment.

        Returns:
            dict: A dictionary containing system and Python related metadata.
        """
        return {
            'hostname': os.uname().nodename,
            'os': platform.system(),
            'os_version': platform.release(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'role_path': os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        }

#---------------------------------------------------------------------------------------
# Process Management
#---------------------------------------------------------------------------------------
class Processor:
    """Main class to process and manage different inspection tasks."""

    @staticmethod
    def process(action, prepend='', append=''):
        """Select and execute the proper action.

        Args:
            action (str): The action to perform.
            prepend (str): String to prepend to messages.
            append (str): String to append to messages.

        Returns:
            dict: Result of the processed action, including any messages, data, and unique identifiers.
        """
        # Generate UUID for this process instance
        process_uuid = str(uuid.uuid4())
        
        # Define order ID (for example sake, we could use a timestamp or incrementing counter)
        order_id = int(datetime.datetime.now().timestamp() * 1000)  # milliseconds since epoch

        result = {
            'uuid': process_uuid,
            'order_id': order_id,
            'msg': '',
            'env': BaseInspection.get_environment_variables(),
            'meta': MetaData.get_metadata(),
            'changed': True,
            'cpu': {}, 
            'memory': {}, 
            'disk': {}, 
            'network': {}, 
            'system': {}, 
            'limits': {}
        }

        if action == 'base-inspection':
            intel_result = BaseInspection.execute()
            result.update(intel_result)  # Update result with all keys from intel_result
            result['msg'] = MessageHandler.format_message(intel_result['msg'], prepend, append)
        else:  # Default to hello_world if no action specified or unknown action
            result['msg'] = MessageHandler.format_message(MessageHandler.hello_world(), prepend, append)
        return result

#---------------------------------------------------------------------------------------
# Module Execution
#---------------------------------------------------------------------------------------
def run_module():
    """Main function to execute the host_inspector module."""
    module_args = dict(
        action=dict(type='str', required=False, default=None),
        prepend=dict(type='str', required=False, default=''),
        append=dict(type='str', required=False, default='')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        params = module.params
        result = Processor.process(params['action'], params['prepend'], params['append'])
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f'An error occurred: {e}')

# Execution Section
if __name__ == '__main__':
    run_module()