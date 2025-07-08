from flask import Flask, request, jsonify

from industrial_fault_system import IndustrialFaultDiagnosisSystem

app = Flask(__name__)
diagnosis_system = IndustrialFaultDiagnosisSystem()


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8866, debug=True)