#!/usr/bin/env python3
"""
Loggin Genie - Decrypt encrypted logs from Kibana/Elasticsearch
"""

import click
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import os

from src.kibana_client import KibanaClient
from src.decryptor import LogDecryptor
from src.formatter import LogFormatter

# Load environment variables
load_dotenv()

console = Console()


def read_logs_from_file(file_path: str) -> list:
    """
    Read logs from a JSON or NDJSON file
    
    Args:
        file_path: Path to the log file
    
    Returns:
        List of log entries in Elasticsearch hit format
    """
    logs = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
        # Try to parse as JSON array first
        try:
            data = json.loads(content)
            
            # If it's already in Elasticsearch format with hits
            if isinstance(data, dict) and 'hits' in data:
                if 'hits' in data['hits']:
                    return data['hits']['hits']
                else:
                    logs = data['hits']
            # If it's a plain array of log objects
            elif isinstance(data, list):
                # Check if first item has Elasticsearch structure
                if data and isinstance(data[0], dict) and '_source' in data[0]:
                    # Already in Elasticsearch format
                    return data
                
                # Convert plain logs to Elasticsearch format
                for i, item in enumerate(data):
                    logs.append({
                        '_id': str(i),
                        '_index': 'file-logs',
                        '_source': item if isinstance(item, dict) else {'message': str(item)}
                    })
            # If it's a single object
            else:
                logs.append({
                    '_id': '0',
                    '_index': 'file-logs',
                    '_source': data
                })
        
        except json.JSONDecodeError:
            # Try NDJSON (newline-delimited JSON)
            for i, line in enumerate(content.split('\n')):
                if line.strip():
                    try:
                        item = json.loads(line)
                        logs.append({
                            '_id': str(i),
                            '_index': 'file-logs',
                            '_source': item if isinstance(item, dict) else {'message': str(item)}
                        })
                    except json.JSONDecodeError:
                        # Plain text line
                        logs.append({
                            '_id': str(i),
                            '_index': 'file-logs',
                            '_source': {'message': line.strip()}
                        })
    
    return logs


@click.command()
@click.option('--kibana-url', 
              envvar='KIBANA_URL',
              help='Kibana URL (can be set via KIBANA_URL env var)')
@click.option('--elasticsearch-url',
              envvar='ELASTICSEARCH_URL', 
              help='Elasticsearch URL (can be set via ELASTICSEARCH_URL env var)')
@click.option('--index', 
              help='Elasticsearch index name (not required when using --file)')
@click.option('--key', 
              envvar='ENCRYPTION_KEY',
              required=True,
              help='Encryption key (can be set via ENCRYPTION_KEY env var)')
@click.option('--algorithm',
              envvar='ENCRYPTION_ALGORITHM',
              default='AES-256-CBC',
              help='Encryption algorithm (default: AES-256-CBC)')
@click.option('--field',
              default='message',
              help='Field name containing encrypted data (default: message)')
@click.option('--query',
              help='Elasticsearch query in JSON format')
@click.option('--size',
              default=100,
              type=int,
              help='Number of logs to fetch (default: 100)')
@click.option('--output',
              type=click.Path(),
              help='Output file path (JSON format)')
@click.option('--format',
              type=click.Choice(['json', 'text', 'table']),
              default='table',
              help='Output format (default: table)')
@click.option('--username',
              envvar='ELASTICSEARCH_USERNAME',
              help='Elasticsearch username')
@click.option('--password',
              envvar='ELASTICSEARCH_PASSWORD',
              help='Elasticsearch password')
@click.option('--api-key',
              envvar='ELASTICSEARCH_API_KEY',
              help='Elasticsearch API key')
@click.option('--file',
              type=click.Path(exists=True),
              help='Read logs from JSON/NDJSON file instead of Kibana')
def main(kibana_url, elasticsearch_url, index, key, algorithm, field, 
         query, size, output, format, username, password, api_key, file):
    """
    Fetch and decrypt encrypted logs from Kibana/Elasticsearch.
    
    Example:
        loggin_genie.py --index "app-logs" --key "your-key" --output decrypted.json
    """
    
    try:
        # Validate inputs
        if not file and not (kibana_url or elasticsearch_url):
            console.print("[red]Error: Either --file, --kibana-url, or --elasticsearch-url must be provided[/red]")
            sys.exit(1)
        
        if not file and not index:
            console.print("[red]Error: --index is required when not using --file[/red]")
            sys.exit(1)
        
        if file and not index:
            # When reading from file, index is optional
            index = "file-logs"
        
        # Parse query if provided
        es_query = None
        if query:
            try:
                es_query = json.loads(query)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON query: {e}[/red]")
                sys.exit(1)
        
        # Fetch logs from file or Kibana
        if file:
            # Read from file
            console.print(f"[cyan]Reading logs from file: {file}[/cyan]")
            logs = read_logs_from_file(file)
            console.print(f"[green]Read {len(logs)} log entries[/green]")
        else:
            # Initialize Kibana client
            console.print("[cyan]Connecting to Elasticsearch/Kibana...[/cyan]")
            client = KibanaClient(
                elasticsearch_url=elasticsearch_url or kibana_url,
                username=username,
                password=password,
                api_key=api_key
            )
            
            # Fetch logs
            console.print(f"[cyan]Fetching logs from index '{index}'...[/cyan]")
            logs = client.fetch_logs(index=index, query=es_query, size=size)
            console.print(f"[green]Fetched {len(logs)} log entries[/green]")
        
        if not logs:
            console.print("[yellow]No logs found[/yellow]")
            return
        
        # Initialize decryptor
        console.print("[cyan]Decrypting logs...[/cyan]")
        decryptor = LogDecryptor(key=key, algorithm=algorithm)
        
        # Decrypt logs
        decrypted_logs = []
        failed_count = 0
        
        for log in logs:
            try:
                # Get the source object
                source = log.get('_source', {})
                encrypted_data = source.get(field)
                
                if encrypted_data:
                    decrypted_data = decryptor.decrypt(encrypted_data)
                    # Preserve original encrypted data and add decrypted version
                    source[f'encrypted_{field}'] = encrypted_data
                    source[f'decrypted_{field}'] = decrypted_data
                    source['_decrypted'] = True
                    log['_source'] = source
                    decrypted_logs.append(log)
                else:
                    console.print(f"[yellow]Warning: Field '{field}' not found in log[/yellow]")
                    decrypted_logs.append(log)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to decrypt log: {e}[/yellow]")
                source['_decryption_error'] = str(e)
                log['_source'] = source
                decrypted_logs.append(log)
                failed_count += 1
        
        console.print(f"[green]Successfully decrypted {len(decrypted_logs) - failed_count} logs[/green]")
        if failed_count > 0:
            console.print(f"[yellow]Failed to decrypt {failed_count} logs[/yellow]")
        
        # Format and output
        formatter = LogFormatter()
        
        if output:
            # Save to file
            output_path = Path(output)
            if format == 'json' or output_path.suffix == '.json':
                formatter.save_json(decrypted_logs, output_path)
                console.print(f"[green]Decrypted logs saved to {output}[/green]")
            else:
                formatter.save_text(decrypted_logs, output_path, field=field)
                console.print(f"[green]Decrypted logs saved to {output}[/green]")
        else:
            # Display in terminal
            if format == 'json':
                formatter.print_json(decrypted_logs)
            elif format == 'text':
                formatter.print_text(decrypted_logs, field=field)
            else:
                formatter.print_table(decrypted_logs, field=field)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
