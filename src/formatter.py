"""
Output formatter for decrypted logs
"""

import json
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from datetime import datetime


class LogFormatter:
    """Format and display decrypted logs"""
    
    def __init__(self):
        self.console = Console()
    
    def print_json(self, logs: List[Dict]):
        """Print logs as formatted JSON"""
        
        json_str = json.dumps(logs, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        self.console.print(syntax)
    
    def print_text(self, logs: List[Dict], field: str = 'message'):
        """Print logs as plain text"""
        
        for i, log in enumerate(logs, 1):
            source = log.get('_source', {})
            timestamp = source.get('@timestamp', source.get('timestamp', 'N/A'))
            message = source.get(field, 'N/A')
            
            self.console.print(f"[cyan]Log #{i}[/cyan] - {timestamp}")
            self.console.print(message)
            self.console.print("-" * 80)
    
    def print_table(self, logs: List[Dict], field: str = 'message', max_width: int = 80):
        """Print logs as a formatted table"""
        
        table = Table(title="Decrypted Logs", show_lines=True)
        
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Timestamp", style="green", width=20)
        table.add_column("Level", style="yellow", width=8)
        table.add_column("Message", style="white", width=max_width)
        
        for i, log in enumerate(logs, 1):
            source = log.get('_source', {})
            
            # Extract fields
            timestamp = source.get('@timestamp', source.get('timestamp', 'N/A'))
            if timestamp != 'N/A':
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            level = source.get('level', source.get('severity', 'INFO'))
            message = source.get(field, 'N/A')
            
            # Truncate long messages
            if isinstance(message, str) and len(message) > max_width:
                message = message[:max_width-3] + "..."
            elif isinstance(message, dict):
                message = json.dumps(message)[:max_width-3] + "..."
            
            # Style level
            if level.upper() == 'ERROR':
                level = f"[red]{level}[/red]"
            elif level.upper() == 'WARN' or level.upper() == 'WARNING':
                level = f"[yellow]{level}[/yellow]"
            else:
                level = f"[green]{level}[/green]"
            
            table.add_row(str(i), timestamp, level, str(message))
        
        self.console.print(table)
    
    def save_json(self, logs: List[Dict], output_path: Path):
        """Save logs as JSON file"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, default=str)
    
    def save_text(self, logs: List[Dict], output_path: Path, field: str = 'message'):
        """Save logs as plain text file"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, log in enumerate(logs, 1):
                source = log.get('_source', {})
                timestamp = source.get('@timestamp', source.get('timestamp', 'N/A'))
                message = source.get(field, 'N/A')
                
                f.write(f"Log #{i} - {timestamp}\n")
                f.write(f"{message}\n")
                f.write("-" * 80 + "\n\n")
    
    def save_csv(self, logs: List[Dict], output_path: Path, fields: List[str] = None):
        """Save logs as CSV file"""
        
        import csv
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not fields:
            fields = ['@timestamp', 'level', 'message']
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for log in logs:
                source = log.get('_source', {})
                row = {field: source.get(field, '') for field in fields}
                writer.writerow(row)
