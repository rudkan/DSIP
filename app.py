from flask import Flask, request, jsonify, send_from_directory
import pymysql
import os

app = Flask(__name__, static_folder='static')

# Utility Function: Get Database Connection
def get_connection():
    db_config = {
        'host': os.getenv('DB_HOST', '172.30.77.56'),  # Use Cluster IP
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'userNPO'),
        'password': os.getenv('DB_PASSWORD', 'vT0ncTXacIq0EUfg'),
        'database': os.getenv('DB_NAME', 'sampledb')
    }
    return pymysql.connect(**db_config)

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
        connection = get_connection()
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
    finally:
        if 'connection' in locals():
            connection.close()

# API Endpoint: Total Entries
@app.route('/analytics/total_entries', methods=['GET'])
def get_total_entries():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM CommunicationDetails")
            result = cursor.fetchone()
        return jsonify({"total": result['total'] if result and 'total' in result else 0}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# API Endpoint: Adults to Kids Ratio
@app.route('/analytics/adults_kids_ratio', methods=['GET'])
def get_adults_kids_ratio():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(NumberOfAdults), 0) AS adults, 
                    COALESCE(SUM(NumberOfChildren), 0) AS kids 
                FROM CommunicationDetails
            """)
            result = cursor.fetchone()
        return jsonify({
            "adults": result[0] if result and result[0] else 0,
            "kids": result[1] if result and result[1] else 0
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# API Endpoint: Recipient Details
@app.route('/analytics/recipient_details', methods=['GET'])
def get_recipient_details_count():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT RecipientDetails, COUNT(*) as count FROM CommunicationDetails GROUP BY RecipientDetails")
            result = cursor.fetchall()
        return jsonify([{"RecipientDetails": row[0], "count": row[1]} for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

# API Endpoint: Get Next Message ID
@app.route('/get_next_message_id', methods=['GET'])
def get_next_message_id():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM CommunicationDetails;")
            result = cursor.fetchone()
            last_message_id = result[0] if result and result[0] else 0
            next_message_id = str(last_message_id + 1)
        return jsonify({"next_message_id": next_message_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
