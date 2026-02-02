"""
Example: Basic usage of Loggin Genie
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kibana_client import KibanaClient
from src.decryptor import LogDecryptor
from src.formatter import LogFormatter


def main():
    # Configuration
    elasticsearch_url = "https://your-elasticsearch-instance.com:9200"
    username = "your-username"
    password = "your-password"
    index = "logs-*"
    encryption_key = "your-encryption-key"
    
    # 1. Connect to Elasticsearch
    print("Connecting to Elasticsearch...")
    client = KibanaClient(
        elasticsearch_url=elasticsearch_url,
        username=username,
        password=password
    )
    
    # 2. Fetch logs
    print("Fetching logs...")
    logs = client.fetch_logs(
        index=index,
        size=10,
        query={"match": {"level": "error"}}  # Optional: filter by error level
    )
    print(f"Fetched {len(logs)} logs")
    
    # 3. Initialize decryptor
    decryptor = LogDecryptor(
        key=encryption_key,
        algorithm='AES-256-CBC'
    )
    
    # 4. Decrypt logs
    print("Decrypting logs...")
    for log in logs:
        encrypted_message = log['_source']['message']
        try:
            decrypted_message = decryptor.decrypt(encrypted_message)
            log['_source']['message'] = decrypted_message
            log['_source']['_decrypted'] = True
            print(f"✓ Decrypted log {log['_id']}")
        except Exception as e:
            print(f"✗ Failed to decrypt log {log['_id']}: {e}")
    
    # 5. Display results
    formatter = LogFormatter()
    formatter.print_table(logs)
    
    # 6. Save to file (optional)
    formatter.save_json(logs, 'decrypted_logs.json')
    print("\nDecrypted logs saved to decrypted_logs.json")
    
    # 7. Close connection
    client.close()


if __name__ == '__main__':
    main()
