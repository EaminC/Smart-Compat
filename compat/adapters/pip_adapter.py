#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pip package manager adapter
"""

import subprocess
from typing import Optional

from .base import PackageManagerAdapter
from ..core.types import PackageInfo


class PipAdapter(PackageManagerAdapter):
    """pip package manager adapter"""
    
    def is_available(self) -> bool:
        try:
            subprocess.run(['pip', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        try:
            result = subprocess.run(
                ['pip', 'show', package_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            dependencies = {}
            if 'Requires' in info and info['Requires']:
                for dep in info['Requires'].split(','):
                    dep = dep.strip()
                    if '==' in dep:
                        name, version = dep.split('==', 1)
                        dependencies[name] = f"=={version}"
                    else:
                        dependencies[dep] = "*"
            
            return PackageInfo(
                name=info.get('Name', package_name),
                version=info.get('Version', ''),
                dependencies=dependencies,
                author=info.get('Author', ''),
                description=info.get('Summary', ''),
                license=info.get('License', ''),
                homepage=info.get('Home-page', '')
            )
            
        except subprocess.CalledProcessError:
            return None
    
    def parse_version_constraint(self, constraint: str) -> str:
        return constraint 