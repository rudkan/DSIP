from flask import Flask, request, jsonify, send_from_directory
import pymysql
import os

app = Flask(__name__, static_folder='static')

# MySQL Configuration (Read from environment variables in OpenShift)
db_config = {
    'host': os.getenv('DB_HOST', '10.128.17.51'),
    'user': os.getenv('DB_USER', 'userNPO'),
    'password': os.getenv('DB_PASSWORD', 'vT0ncTXacIq0EUfg'),
    'database': os.getenv('DB_NAME', 'sampledb')
}

connection = pymysql.connect(**db_config)

# Serve Static Frontend Files
@app.route('/')
def serve_frontend():
    """Serve the main HTML file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve other static files like CSS, JS."""
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

# API Endpoint: Analytics
@app.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_messages, AVG(NumberOfAdults) AS avg_adults FROM CommunicationDetails")
            result = cursor.fetchone()
        return jsonify({
            "total_messages": result[0],
            "avg_adults": result[1]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
