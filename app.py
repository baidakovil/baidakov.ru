import logging  # Import logging after log_config
import os
import sqlite3
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory

from pyscripts import log_config

load_dotenv()

app = Flask(__name__, static_folder='styles', static_url_path='/styles')

logger = log_config.setup_logging()

logger.info('Application startup')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/jsscripts/<path:filename>')
def serve_js(filename):
    return send_from_directory('jsscripts', filename)


@app.route('/api/updates', methods=['GET'])
def get_updates():
    try:
        conn = sqlite3.connect('./db/services.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, formatted_datetime FROM services")
        services = cursor.fetchall()
        conn.close()

        data = [
            {'name': name, 'formatted_datetime': formatted_datetime}
            for name, formatted_datetime in services
        ]
        return jsonify(data)
    except Exception as e:
        logger.error(f'Error fetching updates: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('FLASK_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug, host=host, port=port)
