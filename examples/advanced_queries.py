"""
Example: Advanced query usage with custom Elasticsearch queries
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kibana_client import KibanaClient
from src.decryptor import LogDecryptor
from src.formatter import LogFormatter
from datetime import datetime, timedelta


def main():
    # Configuration
    elasticsearch_url = "https://your-elasticsearch-instance.com:9200"
    api_key = "your-api-key"
    index = "app-logs-*"
    encryption_key = "your-encryption-key"
    
    # Connect to Elasticsearch
    client = KibanaClient(
        elasticsearch_url=elasticsearch_url,
        api_key=api_key
    )
    
    # Example 1: Query logs from the last 24 hours
    print("Example 1: Logs from last 24 hours")
    yesterday = datetime.now() - timedelta(days=1)
    query1 = {
        "bool": {
            "must": [
                {
                    "range": {
                        "@timestamp": {
                            "gte": yesterday.isoformat()
                        }
                    }
                }
            ]
        }
    }
    logs1 = client.fetch_logs(index=index, query=query1, size=50)
    print(f"Found {len(logs1)} logs from last 24 hours\n")
    
    # Example 2: Query error logs from specific service
    print("Example 2: Error logs from 'auth-service'")
    query2 = {
        "bool": {
            "must": [
                {"match": {"level": "error"}},
                {"match": {"service": "auth-service"}}
            ]
        }
    }
    logs2 = client.fetch_logs(index=index, query=query2, size=20)
    print(f"Found {len(logs2)} error logs from auth-service\n")
    
    # Example 3: Query logs with specific keywords
    print("Example 3: Logs containing 'failed' or 'timeout'")
    query3 = {
        "bool": {
            "should": [
                {"match": {"message": "failed"}},
                {"match": {"message": "timeout"}}
            ],
            "minimum_should_match": 1
        }
    }
    logs3 = client.fetch_logs(index=index, query=query3, size=30)
    print(f"Found {len(logs3)} logs with keywords\n")
    
    # Decrypt and display
    decryptor = LogDecryptor(key=encryption_key, algorithm='AES-256-CBC')
    formatter = LogFormatter()
    
    # Process logs from example 2
    print("\nDecrypting error logs...")
    for log in logs2:
        try:
            encrypted_msg = log['_source']['message']
            decrypted_msg = decryptor.decrypt(encrypted_msg)
            log['_source']['message'] = decrypted_msg
        except Exception as e:
            print(f"Failed to decrypt: {e}")
    
    # Display results
    formatter.print_table(logs2)
    
    client.close()


if __name__ == '__main__':
    main()
