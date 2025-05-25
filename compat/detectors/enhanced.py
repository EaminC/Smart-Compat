#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Package Conflict Detector
Integrates pip's dependency resolver with advanced analysis
"""

from typing import Dict, List, Optional, Set
from .hypothetical import HypotheticalConflictDetector
from ..utils.pip_resolver import PipDependencyResolver
from ..utils.version_resolver import VersionConstraintResolver
from ..core.types import ConflictResult, ConflictType, PackageInfo


class EnhancedConflictDetector(HypotheticalConflictDetector):
    """集成pip能力的增强冲突检测器"""
    
    def __init__(self, enable_suggestions: bool = True, use_pip_resolver: bool = True):
        super().__init__(enable_suggestions, hypothetical_mode=True)
        self.use_pip_resolver = use_pip_resolver
        self.pip_resolver = PipDependencyResolver() if use_pip_resolver else None
        self.version_resolver = VersionConstraintResolver()
    
    def detect_enhanced_conflicts(self, package1: str, package2: str) -> ConflictResult:
        """增强的冲突检测，使用pip的依赖解析能力"""
        
        # 首先进行基础检测
        basic_result = self.detect_hypothetical_conflicts(package1, package2)
        
        # 如果基础检测发现了明确的错误（包不存在、版本不存在），直接返回
        if basic_result.conflict_type in [ConflictType.PACKAGE_NOT_FOUND, ConflictType.VERSION_CONFLICT]:
            return basic_result
        
        # 如果启用了pip解析器，进行更精准的冲突检测
        if self.use_pip_resolver and self.pip_resolver:
            pip_result = self._check_with_pip_resolver(package1, package2)
            
            # 如果pip检测到冲突，覆盖基础结果
            if not pip_result.get('success', True):
                return self._create_pip_conflict_result(package1, package2, pip_result)
        
        # 进行增强的版本约束检查
        constraint_result = self._check_version_constraints(package1, package2)
        
        # 如果发现版本约束冲突，更新结果
        if constraint_result.get('has_conflicts'):
            return self._create_constraint_conflict_result(package1, package2, constraint_result)
        
        # 如果没有发现额外冲突，返回基础检测结果，但添加增强信息
        return self._enhance_basic_result(basic_result, pip_result if self.use_pip_resolver else None, constraint_result)
    
    def _check_with_pip_resolver(self, package1: str, package2: str) -> Dict:
        """使用pip解析器检查包组合"""
        try:
            # 模拟pip install两个包
            packages = [package1, package2]
            result = self.pip_resolver.simulate_pip_install(packages)
            
            # 如果模拟安装失败，进一步分析
            if not result.get('success'):
                # 检查版本约束
                constraint_check = self.pip_resolver.check_version_constraints(package1, package2)
                result['constraint_analysis'] = constraint_check
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pip resolver error: {e}',
                'fallback_to_basic': True
            }
    
    def _check_version_constraints(self, package1: str, package2: str) -> Dict:
        """检查版本约束兼容性"""
        try:
            pkg1_name, pkg1_constraint = self.parse_package_spec(package1)
            pkg2_name, pkg2_constraint = self.parse_package_spec(package2)
            
            result = {
                'has_conflicts': False,
                'conflicts': [],
                'constraint_details': {}
            }
            
            # 如果是同一个包的不同约束
            if pkg1_name.lower() == pkg2_name.lower() and pkg1_constraint and pkg2_constraint:
                # 提取约束部分（去掉==, >=等）
                constraint1 = pkg1_constraint
                constraint2 = pkg2_constraint
                
                compatibility = self.version_resolver.check_constraints_compatibility(
                    constraint1, constraint2
                )
                
                if not compatibility.get('compatible', True):
                    result['has_conflicts'] = True
                    result['conflicts'].append({
                        'type': 'version_constraint_incompatible',
                        'package': pkg1_name,
                        'constraint1': constraint1,
                        'constraint2': constraint2,
                        'details': compatibility
                    })
                
                result['constraint_details']['same_package'] = compatibility
            
            # 获取每个约束的解释
            if pkg1_constraint:
                result['constraint_details']['pkg1_explanation'] = self.version_resolver.explain_constraint(pkg1_constraint)
            
            if pkg2_constraint:
                result['constraint_details']['pkg2_explanation'] = self.version_resolver.explain_constraint(pkg2_constraint)
            
            return result
            
        except Exception as e:
            return {
                'has_conflicts': False,
                'error': f'Constraint check error: {e}'
            }
    
    def _create_pip_conflict_result(self, package1: str, package2: str, pip_result: Dict) -> ConflictResult:
        """基于pip解析结果创建冲突结果"""
        
        error_analysis = pip_result.get('error_analysis', {})
        conflict_type = error_analysis.get('conflict_type', 'unknown')
        
        if conflict_type == 'version_conflict':
            conflict_type_enum = ConflictType.VERSION_CONFLICT
            severity = "high"
            message = "Pip dependency resolver detected version conflicts"
        elif conflict_type == 'dependency_resolution_failure':
            conflict_type_enum = ConflictType.DEPENDENCY_CONFLICT
            severity = "high"
            message = "Pip dependency resolver failed to find compatible versions"
        else:
            conflict_type_enum = ConflictType.DEPENDENCY_CONFLICT
            severity = "medium"
            message = "Pip dependency resolver detected conflicts"
        
        # 添加详细的pip错误信息
        if pip_result.get('raw_error'):
            message += f"\n\nPip error details:\n{pip_result['raw_error']}"
        
        return ConflictResult(
            conflict_type=conflict_type_enum,
            message=message,
            severity=severity,
            details={
                'pip_analysis': pip_result,
                'resolver_method': 'pip_simulation',
                'enhanced_detection': True
            }
        )
    
    def _create_constraint_conflict_result(self, package1: str, package2: str, constraint_result: Dict) -> ConflictResult:
        """基于版本约束检查结果创建冲突结果"""
        
        conflicts = constraint_result.get('conflicts', [])
        conflict_messages = []
        
        for conflict in conflicts:
            if conflict['type'] == 'version_constraint_incompatible':
                pkg = conflict['package']
                c1 = conflict['constraint1']
                c2 = conflict['constraint2']
                
                # 获取约束的人类可读解释
                details = constraint_result.get('constraint_details', {})
                c1_explain = details.get('pkg1_explanation', {}).get('human_readable', c1)
                c2_explain = details.get('pkg2_explanation', {}).get('human_readable', c2)
                
                conflict_messages.append(
                    f"Package {pkg} has incompatible version constraints:\n"
                    f"  • Constraint 1: {c1_explain}\n"
                    f"  • Constraint 2: {c2_explain}"
                )
        
        message = "Version constraint conflicts detected:\n" + "\n".join(conflict_messages)
        
        return ConflictResult(
            conflict_type=ConflictType.VERSION_CONFLICT,
            message=message,
            severity="high",
            details={
                'constraint_analysis': constraint_result,
                'resolver_method': 'version_constraint_analysis',
                'enhanced_detection': True
            }
        )
    
    def _enhance_basic_result(self, basic_result: ConflictResult, pip_result: Optional[Dict], constraint_result: Dict) -> ConflictResult:
        """增强基础检测结果，添加pip和约束分析信息"""
        
        enhanced_details = basic_result.details.copy() if basic_result.details else {}
        
        # 添加pip分析结果
        if pip_result:
            enhanced_details['pip_analysis'] = pip_result
            
            # 如果pip认为没有冲突，可以提升信心度
            if pip_result.get('success'):
                enhanced_details['pip_confirmation'] = "Pip dependency resolver confirms no conflicts"
        
        # 添加版本约束分析
        enhanced_details['constraint_analysis'] = constraint_result
        
        # 标记为增强检测
        enhanced_details['enhanced_detection'] = True
        enhanced_details['detection_methods'] = ['hypothetical', 'system_level', 'transitive']
        
        if pip_result:
            enhanced_details['detection_methods'].append('pip_simulation')
        
        enhanced_details['detection_methods'].append('version_constraint_analysis')
        
        # 如果原本是无冲突，且有pip确认，可以增加信心度描述
        if (basic_result.conflict_type == ConflictType.NO_CONFLICT and 
            pip_result and pip_result.get('success')):
            
            enhanced_message = basic_result.message + "\n\n✅ Confirmed by pip dependency resolver"
        else:
            enhanced_message = basic_result.message
        
        return ConflictResult(
            conflict_type=basic_result.conflict_type,
            message=enhanced_message,
            severity=basic_result.severity,
            details=enhanced_details
        ) 