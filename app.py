"""
Flask Web Interface for Outlook Bulk Mail Bot
"""
from flask import Flask, render_template, request, jsonify
import os
import asyncio
import logging
from dotenv import load_dotenv
from services.outlook_service import OutlookMailService
from services.scheduler import MailScheduler

load_dotenv()

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Store scheduler globally
scheduler = None

@app.route('/')
def index():
    """Homepage with bot control panel"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the mail bot"""
    try:
        data = request.json
        
        # Get credentials from form
        client_email = data.get('client_email', '')
        client_password = data.get('client_password', '')
        recipients = data.get('recipients', [])
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        # Validate inputs
        if not client_email or not client_password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400
        
        if not recipients or len(recipients) == 0:
            return jsonify({'status': 'error', 'message': 'At least one recipient is required'}), 400
        
        if not subject or not message:
            return jsonify({'status': 'error', 'message': 'Subject and message are required'}), 400
        
        # Initialize Outlook service with user credentials
        outlook_service = OutlookMailService(
            email=client_email,
            password=client_password,
            # Or use these if you have them configured:
            client_id=os.getenv('MICROSOFT_CLIENT_ID'),
            client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
            tenant_id=os.getenv('MICROSOFT_TENANT_ID')
        )
        
        # Schedule emails
        scheduler = MailScheduler(outlook_service)
        result = asyncio.run(scheduler.send_bulk_mail(recipients, subject, message))
        
        return jsonify({
            'status': 'success',
            'message': f'Emails sent successfully to {len(recipients)} recipient(s)!',
            'result': result
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Check bot status"""
    return jsonify({
        'status': 'running',
        'bot_type': 'web',
        'client_id_set': bool(os.getenv('MICROSOFT_CLIENT_ID'))
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
