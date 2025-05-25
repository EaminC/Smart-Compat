#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
npm package manager adapter
"""

import subprocess
import json
from typing import Optional

from .base import PackageManagerAdapter
from ..core.types import PackageInfo


class NpmAdapter(PackageManagerAdapter):
    """npm package manager adapter"""
    
    def is_available(self) -> bool:
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        try:
            result = subprocess.run(
                ['npm', 'view', package_name, '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            
            # Handle npm view returned data structure
            if isinstance(data, list):
                data = data[-1]  # Take latest version
            
            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})
            peer_dependencies = data.get('peerDependencies', {})
            
            return PackageInfo(
                name=data.get('name', package_name),
                version=data.get('version', ''),
                dependencies=dependencies,
                dev_dependencies=dev_dependencies,
                peer_dependencies=peer_dependencies,
                author=str(data.get('author', {})) if isinstance(data.get('author'), dict) else data.get('author', ''),
                description=data.get('description', ''),
                license=data.get('license', ''),
                homepage=data.get('homepage', '')
            )
            
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None
    
    def parse_version_constraint(self, constraint: str) -> str:
        # npm version constraint parsing
        return constraint 