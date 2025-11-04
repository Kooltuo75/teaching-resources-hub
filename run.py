"""
Entry point for the Teaching Resources application.
Run this file to start the web server.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Teaching Resources Hub...")
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
