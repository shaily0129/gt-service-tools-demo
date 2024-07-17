from setuptools import setup, find_packages
from setuptools.command.install import install as _install
import os
import yaml

packageName = 'dataGenerator'
version = '0.1'

class CustomInstall(_install):
    def run(self):
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dataGenerator_config.yaml')
        
        # Check if the config file already exists and read the version
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                config_data = yaml.safe_load(config_file)
                existing_version = config_data.get('version', None)
                
                # Check if the existing version matches the current version
                if existing_version == version:
                    print(f"Version {existing_version} already installed, skipping installation.")
                    return
                else:
                    print(f"Updating from version {existing_version} to {version}")
        
        # Proceed with the rest of the installation
        _install.run(self)
        
        # Only write the config file if it doesn't exist or needs updating
        config_content = {
            'version': '0.1',
            'format': 'yaml',
            'output_path': './data/scenario_data/',
            'output_filename_prefix': 'scenario_',
            'scenarios_path': './dataSchemas/_scenarios/test_scenarios_1.yaml',
            'specific_scenario_ids': []
        }
        with open(config_path, 'w') as config_file:
            yaml.dump(config_content, config_file)
        print(f"Config file created/updated at {config_path}")

setup(
    name='packageName',
    version=version,
    packages=find_packages(),
    cmdclass={
        'install': CustomInstall,
    },
    # include any other necessary setup kwargs
)