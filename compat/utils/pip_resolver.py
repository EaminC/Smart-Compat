#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pip Dependency Resolver Integration
Integrates with pip's dependency resolution for accurate conflict detection
"""

import subprocess
import json
import tempfile
import os
import re
from typing import Dict, List, Optional, Tuple, Set
from ..core.types import ConflictResult, ConflictType


class PipDependencyResolver:
    """基于pip的依赖解析器"""
    
    def __init__(self):
        self.temp_dir = None
    
    def check_installation_feasibility(self, packages: List[str]) -> Dict:
        """检查包组合是否可以成功安装（使用pip的依赖解析）"""
        try:
            # 创建临时虚拟环境来测试
            with tempfile.TemporaryDirectory() as temp_dir:
                venv_path = os.path.join(temp_dir, 'test_env')
                
                # 创建虚拟环境
                subprocess.run([
                    'python', '-m', 'venv', venv_path
                ], check=True, capture_output=True)
                
                # 获取虚拟环境的pip路径
                if os.name == 'nt':  # Windows
                    pip_path = os.path.join(venv_path, 'Scripts', 'pip')
                else:  # Unix/Linux/Mac
                    pip_path = os.path.join(venv_path, 'bin', 'pip')
                
                # 使用--dry-run模拟安装
                cmd = [pip_path, 'install', '--dry-run'] + packages
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Pip dependency resolution timed out',
                'timeout': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to test installation: {e}'
            }
    
    def get_dependency_tree(self, package: str) -> Dict:
        """获取包的依赖树"""
        try:
            # 使用pipdeptree if available, otherwise use pip show
            try:
                result = subprocess.run([
                    'pipdeptree', '--json-tree', '--packages', package
                ], capture_output=True, text=True, check=True)
                
                return {
                    'success': True,
                    'tree': json.loads(result.stdout)
                }
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to pip show
                return self._get_dependency_tree_pip_show(package)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get dependency tree: {e}'
            }
    
    def _get_dependency_tree_pip_show(self, package: str) -> Dict:
        """使用pip show获取依赖信息（fallback方法）"""
        try:
            result = subprocess.run([
                'pip', 'show', package
            ], capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            dependencies = []
            
            for line in lines:
                if line.startswith('Requires:'):
                    deps_str = line.split(':', 1)[1].strip()
                    if deps_str:
                        dependencies = [dep.strip() for dep in deps_str.split(',')]
                    break
            
            return {
                'success': True,
                'dependencies': dependencies,
                'method': 'pip_show'
            }
            
        except subprocess.CalledProcessError:
            return {
                'success': False,
                'error': f'Package {package} not found'
            }
    
    def check_version_constraints(self, package1: str, package2: str) -> Dict:
        """检查两个包的版本约束是否兼容"""
        try:
            # 解析包规格
            pkg1_name, pkg1_constraint = self._parse_package_spec(package1)
            pkg2_name, pkg2_constraint = self._parse_package_spec(package2)
            
            # 如果是同一个包的不同版本约束
            if pkg1_name.lower() == pkg2_name.lower():
                if pkg1_constraint and pkg2_constraint:
                    compatible = self._check_constraint_compatibility(
                        pkg1_constraint, pkg2_constraint
                    )
                    return {
                        'same_package': True,
                        'compatible': compatible,
                        'constraint1': pkg1_constraint,
                        'constraint2': pkg2_constraint
                    }
            
            # 检查是否有共同的依赖冲突
            dep_tree1 = self.get_dependency_tree(pkg1_name)
            dep_tree2 = self.get_dependency_tree(pkg2_name)
            
            conflicts = self._find_dependency_conflicts(dep_tree1, dep_tree2)
            
            return {
                'same_package': False,
                'dependency_conflicts': conflicts,
                'pkg1_deps': dep_tree1,
                'pkg2_deps': dep_tree2
            }
            
        except Exception as e:
            return {
                'error': f'Failed to check version constraints: {e}'
            }
    
    def _parse_package_spec(self, package_spec: str) -> Tuple[str, Optional[str]]:
        """解析包规格为包名和版本约束"""
        # 支持各种版本操作符
        operators = ['~=', '>=', '<=', '!=', '==', '>', '<']
        
        for op in operators:
            if op in package_spec:
                name, version = package_spec.split(op, 1)
                return name.strip(), f"{op}{version.strip()}"
        
        return package_spec.strip(), None
    
    def _check_constraint_compatibility(self, constraint1: str, constraint2: str) -> bool:
        """检查两个版本约束是否兼容"""
        # 这里可以实现更复杂的版本约束兼容性检查
        # 暂时简化为相等检查
        return constraint1 == constraint2
    
    def _find_dependency_conflicts(self, dep_tree1: Dict, dep_tree2: Dict) -> List[Dict]:
        """查找依赖树中的冲突"""
        conflicts = []
        
        if not (dep_tree1.get('success') and dep_tree2.get('success')):
            return conflicts
        
        # 提取依赖列表
        deps1 = dep_tree1.get('dependencies', [])
        deps2 = dep_tree2.get('dependencies', [])
        
        # 找到共同依赖
        deps1_parsed = {self._parse_package_spec(dep)[0]: dep for dep in deps1}
        deps2_parsed = {self._parse_package_spec(dep)[0]: dep for dep in deps2}
        
        common_deps = set(deps1_parsed.keys()) & set(deps2_parsed.keys())
        
        for dep_name in common_deps:
            dep1_spec = deps1_parsed[dep_name]
            dep2_spec = deps2_parsed[dep_name]
            
            if dep1_spec != dep2_spec:
                conflicts.append({
                    'dependency': dep_name,
                    'constraint1': dep1_spec,
                    'constraint2': dep2_spec,
                    'type': 'version_constraint_conflict'
                })
        
        return conflicts
    
    def simulate_pip_install(self, packages: List[str]) -> Dict:
        """模拟pip install过程，检查是否会有冲突"""
        try:
            # 使用pip install --dry-run --report来获取详细信息
            cmd = ['pip', 'install', '--dry-run', '--quiet'] + packages
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 分析输出
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'No conflicts detected by pip resolver',
                    'output': result.stdout
                }
            else:
                # 解析错误信息
                error_analysis = self._analyze_pip_error(result.stderr)
                return {
                    'success': False,
                    'conflicts_detected': True,
                    'error_analysis': error_analysis,
                    'raw_error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Pip simulation timed out (complex dependency resolution)',
                'timeout': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to simulate pip install: {e}'
            }
    
    def _analyze_pip_error(self, error_output: str) -> Dict:
        """分析pip错误输出，提取冲突信息"""
        analysis = {
            'conflict_type': 'unknown',
            'conflicting_packages': [],
            'version_conflicts': [],
            'dependency_conflicts': []
        }
        
        lines = error_output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 检测版本冲突
            if 'but you have' in line.lower() or 'incompatible' in line.lower():
                analysis['conflict_type'] = 'version_conflict'
                # 提取包名和版本信息
                # 这里可以进一步解析具体的冲突信息
            
            # 检测依赖解析失败
            elif 'could not find a version' in line.lower():
                analysis['conflict_type'] = 'dependency_resolution_failure'
            
            # 检测循环依赖
            elif 'circular dependency' in line.lower():
                analysis['conflict_type'] = 'circular_dependency'
        
        return analysis 