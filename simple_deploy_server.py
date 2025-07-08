#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版故障诊断 Web 服务
使用简化版故障诊断系统，避免 PaddleHub 依赖问题
"""

from flask import Flask, request, jsonify
from simple_fault_system import SimpleFaultDiagnosisSystem

app = Flask(__name__)
diagnosis_system = SimpleFaultDiagnosisSystem()


@app.route('/diagnose', methods=['POST'])
def diagnose_api():
    """诊断API接口"""
    try:
        data = request.get_json()
        user_input = data.get('text', '')

        if not user_input:
            return jsonify({'error': '输入文本不能为空'}), 400

        # 执行诊断
        result = diagnosis_system.diagnose(user_input)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '简化版故障诊断系统运行正常'
    })


@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'message': '简化版工业故障诊断系统',
        'version': '1.0.0',
        'endpoints': {
            'diagnose': '/diagnose (POST)',
            'health': '/health (GET)'
        },
        'usage': {
            'diagnose': 'POST /diagnose with {"text": "故障描述"}'
        }
    })


if __name__ == '__main__':
    print("启动简化版故障诊断系统...")
    print("服务地址: http://localhost:8866")
    print("API文档: http://localhost:8866/")
    app.run(host='0.0.0.0', port=8866, debug=True) 