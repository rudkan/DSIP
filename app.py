from flask import Flask, request, jsonify, send_from_directory
import pymysql
import os

app = Flask(__name__, static_folder='static')

# MySQL Configuration (Read from environment variables in OpenShift)
db_config = {
    'host': os.getenv('DB_HOST', '10.128.38.157'),
    'user': os.getenv('DB_USER', 'userNPO'),
    'password': os.getenv('DB_PASSWORD', 'vT0ncTXacIq0EUfg'),
    'database': os.getenv('DB_NAME', 'sampledb')
}

connection = pymysql.connect(**db_config)

# Serve Static Frontend Files
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# API Endpoint: Submit Data
@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO CommunicationDetails (
                MessageID, SenderDetails, RecipientDetails, Date, Medium, SourceLocation,
                DestinationLocation, CommunicationType, NumberOfAdults, NumberOfChildren,
                EventType, EventNotes, VictimEntity, VictimAction, VictimOutcome,
                OtherEntityName, OtherEntityAction, OtherEntityOutcome, SpecificLocation, LocationContext
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                data['MessageID'], data['SenderDetails'], data['RecipientDetails'], data['Date'],
                data['Medium'], data['SourceLocation'], data['DestinationLocation'], data['CommunicationType'],
                data['NumberOfAdults'], data['NumberOfChildren'], data['EventType'], data['EventNotes'],
                data['VictimEntity'], data['VictimAction'], data['VictimOutcome'], data['OtherEntityName'],
                data['OtherEntityAction'], data['OtherEntityOutcome'], data['SpecificLocation'], data['LocationContext']
            ))
            connection.commit()
        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Endpoint: Event Type Analysis
@app.route('/analytics/event_type', methods=['GET'])
def get_event_type_analysis():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EventType, COUNT(*) as count FROM CommunicationDetails GROUP BY EventType")
            result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Endpoint: Communication Trends Over Time
@app.route('/analytics/trend', methods=['GET'])
def get_communication_trend():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATE(Date) as communication_date, COUNT(*) as count FROM CommunicationDetails GROUP BY DATE(Date)")
            result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Endpoint: Medium Usage Analysis
@app.route('/analytics/medium', methods=['GET'])
def get_medium_analysis():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Medium, COUNT(*) as count FROM CommunicationDetails GROUP BY Medium")
            result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
