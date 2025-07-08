#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版工业故障诊断系统
使用 jieba 替代 PaddleHub，避免复杂的依赖问题
"""

import jieba
import jieba.posseg as pseg
import pandas as pd
import json
import re
from typing import List, Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify


class SimpleFaultDiagnosisSystem:
    """简化版工业互联网故障诊断系统"""

    def __init__(self):
        # 设置自定义词典
        self.setup_custom_dict()
        
        # 初始化数据库连接（这里用字典模拟）
        self.device_master = {}  # 设备主表
        self.component_master = {}  # 部件主表
        self.inspection_data = []  # 点检数据
        self.hazard_data = []  # 隐患数据
        self.maintenance_data = []  # 维修数据

    def setup_custom_dict(self):
        """设置工业设备专用词典"""
        # 创建自定义词典文件
        custom_dict_content = """  
轧机/n  
制动力/n  
润滑系统/n  
轧辊/n  
电机自由端/n  
振动/n  
包络谱/n  
轴承外圈/n  
430号轧机/n  
排污泵/n  
管道排气阀/n  
叶轮堵塞/n
保持架/n  
        """

        with open('industrial_dict.txt', 'w', encoding='utf-8') as f:
            f.write(custom_dict_content.strip())

        # 加载自定义词典
        jieba.load_userdict('industrial_dict.txt')

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """提取文本中的关键实体信息（使用 jieba 替代 LAC）"""
        # 使用 jieba 进行词性标注
        words = pseg.cut(text)

        entities = {
            'device_names': [],  # 设备名称
            'fault_locations': [],  # 故障部位
            'fault_phenomena': [],  # 故障现象
            'time_info': [],  # 时间信息
            'technical_terms': []  # 技术术语
        }

        for word, flag in words:
            # 识别设备名称（包含"机"、"泵"、"阀"等关键词）
            if 'n' in flag and any(keyword in word for keyword in ['机', '泵', '阀']) and len(word) > 2:
                entities['device_names'].append(word)

            # 识别故障部位
            if 'n' in flag and any(keyword in word for keyword in ['系统', '部位', '端', '轴承', '轧辊', '保持架']):
                entities['fault_locations'].append(word)

            # 识别时间信息
            if flag == 't' or re.match(r'\d+[月日时分]', word):
                entities['time_info'].append(word)

            # 识别技术术语
            if 'n' in flag and any(keyword in word for keyword in ['力', '谱', '振动', '温度']):
                entities['technical_terms'].append(word)

        return entities

    def classify_text_type(self, text: str) -> str:
        """分类文本属于点检、隐患还是维修类型"""
        # 定义关键词规则
        inspection_keywords = ['点检', '检查', '巡检', '监测', '状态']
        hazard_keywords = ['隐患', '异常', '故障', '报警', '问题']
        maintenance_keywords = ['维修', '检修', '保养', '更换', '修复']

        # 统计关键词出现次数
        inspection_count = sum(1 for keyword in inspection_keywords if keyword in text)
        hazard_count = sum(1 for keyword in hazard_keywords if keyword in text)
        maintenance_count = sum(1 for keyword in maintenance_keywords if keyword in text)

        # 根据关键词数量判断类型
        if hazard_count >= max(inspection_count, maintenance_count):
            return "隐患"
        elif maintenance_count >= inspection_count:
            return "维修"
        else:
            return "点检"

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感倾向，判断故障严重程度（简化版）"""
        # 定义严重程度关键词
        severe_keywords = ['严重', '紧急', '危险', '故障', '异常', '报警']
        moderate_keywords = ['问题', '异常', '波动', '不稳定']
        mild_keywords = ['轻微', '小问题', '注意', '观察']

        severe_count = sum(1 for keyword in severe_keywords if keyword in text)
        moderate_count = sum(1 for keyword in moderate_keywords if keyword in text)
        mild_count = sum(1 for keyword in mild_keywords if keyword in text)

        if severe_count > 0:
            return {'label': '严重', 'confidence': 0.8}
        elif moderate_count > 0:
            return {'label': '中等', 'confidence': 0.6}
        elif mild_count > 0:
            return {'label': '轻微', 'confidence': 0.4}
        else:
            return {'label': '正常', 'confidence': 0.2}

    def query_knowledge_base(self, entities: Dict[str, Any], text_type: str) -> Dict[str, Any]:
        """根据实体信息查询相关知识库"""
        results = {
            'matched_records': [],
            'recommendations': [],
            'risk_level': 'low'
        }

        device_names = entities.get('device_names', [])
        fault_locations = entities.get('fault_locations', [])

        if text_type == "点检":
            # 查询点检记录
            for record in self.inspection_data:
                if any(device in record.get('device_name', '') for device in device_names):
                    results['matched_records'].append(record)

        elif text_type == "隐患":
            # 查询隐患记录
            for record in self.hazard_data:
                if any(device in record.get('device_name', '') for device in device_names):
                    results['matched_records'].append(record)
                    # 根据隐患等级设置风险级别
                    if record.get('danger_level') in ['A类', 'B类']:
                        results['risk_level'] = 'high'

        elif text_type == "维修":
            # 查询维修记录
            for record in self.maintenance_data:
                if any(device in record.get('repair_equipment', '') for device in device_names):
                    results['matched_records'].append(record)

        return results

    def generate_recommendations(self, entities: Dict[str, Any],
                                 knowledge_results: Dict[str, Any]) -> List[str]:
        """生成维护建议"""
        recommendations = []

        # 基于历史记录生成建议
        for record in knowledge_results['matched_records']:
            if 'process_measure' in record:
                recommendations.append(f"建议采取措施: {record['process_measure']}")
            if 'guard_measure' in record:
                recommendations.append(f"监护措施: {record['guard_measure']}")

        # 基于故障部位生成通用建议
        fault_locations = entities.get('fault_locations', [])
        for location in fault_locations:
            if '轴承' in location:
                recommendations.append("建议检查轴承润滑情况，监测振动和温度变化")
            elif '润滑系统' in location:
                recommendations.append("建议检查润滑油位和油质，清洁过滤器")
            elif '轧辊' in location:
                recommendations.append("建议检查轧辊磨损情况，必要时进行更换")
            elif '保持架' in location:
                recommendations.append("建议检查保持架的状态，检测对应的情况")

        return list(set(recommendations))  # 去重

    def diagnose(self, user_input: str) -> Dict[str, Any]:
        """主要诊断流程"""
        # 1. 实体识别
        entities = self.extract_entities(user_input)

        # 2. 文本分类
        text_type = self.classify_text_type(user_input)

        # 3. 情感分析（判断严重程度）
        sentiment = self.analyze_sentiment(user_input)

        # 4. 知识库查询
        knowledge_results = self.query_knowledge_base(entities, text_type)

        # 5. 生成建议
        recommendations = self.generate_recommendations(entities, knowledge_results)

        # 6. 构建诊断报告
        diagnosis_report = {
            'input_text': user_input,
            'extracted_entities': entities,
            'text_classification': text_type,
            'sentiment_analysis': sentiment,
            'matched_records': knowledge_results['matched_records'],
            'risk_level': knowledge_results['risk_level'],
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }

        return diagnosis_report

    def format_output(self, diagnosis_report: Dict[str, Any]) -> str:
        """格式化输出诊断结果"""
        output = f"""  
=== 工业设备故障诊断报告 ===  
输入文本: {diagnosis_report['input_text']}  
分类结果: {diagnosis_report['text_classification']}  
风险等级: {diagnosis_report['risk_level']}  

识别的关键信息:  
- 设备名称: {', '.join(diagnosis_report['extracted_entities']['device_names'])}  
- 故障部位: {', '.join(diagnosis_report['extracted_entities']['fault_locations'])}  
- 技术术语: {', '.join(diagnosis_report['extracted_entities']['technical_terms'])}  

维护建议:  
"""
        for i, rec in enumerate(diagnosis_report['recommendations'], 1):
            output += f"{i}. {rec}\n"

        output += f"\n匹配到 {len(diagnosis_report['matched_records'])} 条相关历史记录"
        output += f"\n生成时间: {diagnosis_report['timestamp']}"

        return output


def main():
    """主函数"""
    # 初始化诊断系统
    diagnosis_system = SimpleFaultDiagnosisSystem()

    # 加载示例数据（实际使用时从数据库加载）
    diagnosis_system.hazard_data = [
        {
            'device_name': '2#棒-17H轧机机列-430',
            'danger_description': '135机组#1机凝汽器坑排污泵出力不足',
            'danger_cause': '叶轮堵塞',
            'process_measure': '水泵拆检，清理杂物',
            'guard_measure': '系统隔离',
            'danger_level': 'D类'
        }
    ]

    # 测试用例
    test_cases = [
        "检修员小明在5月5日9:00发现430号轧机制动力出现异常波动",
        "电机自由端H测点包络谱轴承外圈特征触发报警",
        "需要对轧机进行定期维修保养"
    ]

    for test_input in test_cases:
        print(f"\n{'=' * 50}")
        print(f"测试输入: {test_input}")

        # 执行诊断
        result = diagnosis_system.diagnose(test_input)

        # 输出结果
        formatted_output = diagnosis_system.format_output(result)
        print(formatted_output)


if __name__ == "__main__":
    main() 