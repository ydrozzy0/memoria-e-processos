from flask import Flask, jsonify, render_template, request
import psutil
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stats')
def stats():
    try:
        
        regex_filter = request.args.get('regex', '')
        pattern = None
        if regex_filter:
            try:
                pattern = re.compile(regex_filter, re.IGNORECASE)
            except re.error as e:
                return jsonify({'error': f'Regex inválida: {str(e)}'}), 400

        
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        
        processes = []
        for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
            try:
                info = proc.info
                name = info['name'] or 'Desconhecido'
                pid = info['pid']
                mem_rss = info['memory_info'].rss if info['memory_info'] else 0

                
                if pattern and not pattern.search(name):
                    continue

                processes.append({
                    'name': name,
                    'pid': pid,
                    'mem_bytes': mem_rss
                })

            except Exception as e:
                print(f"Erro ao ler processo: {e}")
                continue

        
        sorted_processes = sorted(processes, key=lambda x: x['mem_bytes'], reverse=True)

        return jsonify({
            'ram': {
                'total': mem.total,
                'used': mem.used,
                'free': mem.available
            },
            'hd': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free
            },
            'processes': sorted_processes
        })

    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
