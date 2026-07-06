import os
import sys

# Add the 'api' directory to the path so we can import index
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from index import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Smart Aquarium server locally on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
