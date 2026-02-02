#!/usr/bin/env python3
"""Generate a large test file with 200+ encrypted Kibana logs"""

import json
import random
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

# Encryption key
KEY = bytes.fromhex('04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948')

def encrypt_aes_cbc(plaintext, key):
    """Encrypt with AES-256-CBC"""
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return f"{iv}:{ct}"

# Services and their typical messages
SERVICES = {
    'user-service': [
        'User login successful for user {}',
        'User registration completed for email {}',
        'Password reset requested for user {}',
        'User profile updated for user {}',
        'Session expired for user {}',
        'Failed login attempt for user {}',
        'User logout completed for user {}',
        'Email verification sent to {}',
        'Two-factor authentication enabled for user {}',
        'Account locked due to suspicious activity for user {}',
        'User preferences updated for user {}',
        'Avatar uploaded successfully for user {}',
    ],
    'auth-service': [
        'JWT token generated for user {}',
        'Token validation successful for user {}',
        'Token expired for user {}',
        'Refresh token issued for user {}',
        'OAuth authentication successful for provider {}',
        'API key validated for client {}',
        'Permission denied for user {} attempting to access {}',
        'Role assignment updated for user {}',
        'Session timeout configured for user {}',
        'MFA code sent to {} via SMS',
        'Biometric authentication successful for user {}',
    ],
    'payment-service': [
        'Payment processed successfully for order {} - Amount: ${}',
        'Payment failed for order {} - Reason: {}',
        'Refund initiated for transaction {}',
        'Subscription renewed for customer {}',
        'Credit card added for customer {}',
        'Payment method updated for customer {}',
        'Invoice generated for order {}',
        'Chargeback received for transaction {}',
        'Recurring payment scheduled for customer {}',
        'Payment gateway timeout for order {}',
        'Fraud detection triggered for transaction {}',
    ],
    'notification-service': [
        'Email notification sent to {}',
        'SMS notification delivered to {}',
        'Push notification sent to device {}',
        'Email delivery failed for {}',
        'Notification preference updated for user {}',
        'Batch notifications sent to {} users',
        'Webhook notification sent to {}',
        'In-app notification displayed for user {}',
        'Newsletter subscription confirmed for {}',
        'Notification template updated: {}',
    ],
    'analytics-service': [
        'Event tracked: {} for user {}',
        'Conversion funnel step {} completed by user {}',
        'A/B test variant {} assigned to user {}',
        'Custom metric recorded: {} = {}',
        'User behavior tracked: {} spent {} minutes on page {}',
        'Analytics report generated for period {}',
        'Dashboard metrics refreshed for {}',
        'Real-time analytics updated for event {}',
        'User segment created: {}',
        'Campaign performance tracked: {} with CTR {}%',
    ],
    'inventory-service': [
        'Stock updated for product {}: {} units available',
        'Low stock alert for product {}',
        'Product {} added to warehouse {}',
        'Inventory sync completed for {} products',
        'Backorder created for product {}',
        'Warehouse transfer initiated: {} units of product {} from {} to {}',
        'Stock count discrepancy detected for product {}',
        'Product {} marked as out of stock',
        'Inventory reservation created for order {}',
        'Bulk import completed: {} products updated',
    ],
    'order-service': [
        'Order {} created by customer {}',
        'Order {} status updated to {}',
        'Order {} shipped via {} - Tracking: {}',
        'Order {} delivered successfully',
        'Order {} cancelled by customer {}',
        'Order {} payment pending',
        'Shipping address updated for order {}',
        'Order {} processing started',
        'Backordered items added to order {}',
        'Order {} expedited shipping applied',
    ],
    'search-service': [
        'Search query executed: "{}" - {} results found',
        'Search index updated with {} documents',
        'Autocomplete suggestions generated for query "{}"',
        'Search filter applied: {} by user {}',
        'Popular search terms updated for period {}',
        'Search relevance tuning applied for category {}',
        'Zero results query logged: "{}"',
        'Search performance: query "{}" took {}ms',
        'Faceted search executed with {} filters',
        'Search synonym mapping updated',
    ],
}

# Log levels with weights
LOG_LEVELS = ['INFO', 'WARN', 'ERROR', 'DEBUG']
LEVEL_WEIGHTS = [60, 20, 15, 5]  # INFO is most common

# Indices
INDICES = ['logs-production-2026.02', 'logs-staging-2026.02', 'logs-production-2026.01']

# Sample data for formatting
USERNAMES = ['alice', 'bob', 'charlie', 'diana', 'edward', 'fiona', 'george', 'helen', 'ivan', 'julia',
             'kevin', 'laura', 'michael', 'nancy', 'oliver', 'patricia', 'quinn', 'rachel', 'samuel', 'tina']
EMAILS = [f'{u}@example.com' for u in USERNAMES]
PRODUCTS = ['laptop', 'smartphone', 'headphones', 'keyboard', 'mouse', 'monitor', 'tablet', 'camera', 'speaker', 'charger']
ORDERS = [f'ORD-{1000+i}' for i in range(100)]
TRANSACTIONS = [f'TXN-{2000+i}' for i in range(100)]
ERROR_REASONS = ['Insufficient funds', 'Card declined', 'Gateway timeout', 'Invalid CVV', 'Expired card']
EVENTS = ['page_view', 'button_click', 'form_submit', 'video_play', 'download', 'share', 'add_to_cart', 'checkout']
PAGES = ['/home', '/products', '/checkout', '/profile', '/search', '/cart', '/help', '/about']
SEARCH_QUERIES = ['laptop deals', 'wireless headphones', 'gaming mouse', 'office chair', '4k monitor', 'usb-c cable']

def generate_message(service):
    """Generate a realistic log message for the service"""
    template = random.choice(SERVICES[service])
    
    # Fill in template placeholders
    if service == 'user-service':
        return template.format(random.choice(USERNAMES))
    elif service == 'auth-service':
        if 'provider' in template:
            return template.format(random.choice(['Google', 'Facebook', 'GitHub']))
        elif 'attempting to access' in template:
            return template.format(random.choice(USERNAMES), random.choice(PAGES))
        elif 'client' in template:
            return template.format(f'CLIENT-{random.randint(1000,9999)}')
        else:
            return template.format(random.choice(USERNAMES))
    elif service == 'payment-service':
        if 'Amount' in template:
            return template.format(random.choice(ORDERS), f'{random.randint(10, 500):.2f}')
        elif 'Reason' in template:
            return template.format(random.choice(ORDERS), random.choice(ERROR_REASONS))
        elif 'customer' in template:
            return template.format(random.choice(USERNAMES))
        else:
            return template.format(random.choice(TRANSACTIONS))
    elif service == 'notification-service':
        if 'device' in template:
            return template.format(f'DEVICE-{random.randint(1000,9999)}')
        elif 'users' in template:
            return template.format(random.randint(10, 1000))
        elif 'template' in template:
            return template.format(random.choice(['welcome_email', 'order_confirmation', 'password_reset']))
        else:
            return template.format(random.choice(EMAILS))
    elif service == 'analytics-service':
        if 'Event tracked' in template:
            return template.format(random.choice(EVENTS), random.choice(USERNAMES))
        elif 'funnel step' in template:
            return template.format(random.randint(1, 5), random.choice(USERNAMES))
        elif 'variant' in template:
            return template.format(random.choice(['A', 'B']), random.choice(USERNAMES))
        elif 'Custom metric' in template:
            return template.format(random.choice(['conversion_rate', 'avg_session_time', 'bounce_rate']), 
                                 f'{random.uniform(0.1, 100):.2f}')
        elif 'spent' in template:
            return template.format(random.choice(USERNAMES), random.randint(1, 60), random.choice(PAGES))
        elif 'report' in template:
            return template.format('January 2026')
        elif 'Dashboard' in template:
            return template.format(random.choice(['sales', 'users', 'traffic']))
        elif 'event' in template:
            return template.format(random.choice(EVENTS))
        elif 'segment' in template:
            return template.format(random.choice(['high_value_customers', 'returning_users', 'new_signups']))
        else:
            return template.format(random.choice(['Summer Sale', 'Email Campaign']), f'{random.uniform(0.5, 10):.1f}')
    elif service == 'inventory-service':
        if 'updated' in template or 'available' in template:
            return template.format(random.choice(PRODUCTS), random.randint(0, 500))
        elif 'alert' in template or 'Backorder' in template or 'out of stock' in template:
            return template.format(random.choice(PRODUCTS))
        elif 'warehouse' in template and 'added' in template:
            return template.format(random.choice(PRODUCTS), f'WH-{random.randint(1,5)}')
        elif 'sync' in template or 'import' in template:
            return template.format(random.randint(50, 500))
        elif 'transfer' in template:
            return template.format(random.randint(10, 100), random.choice(PRODUCTS), 
                                 f'WH-{random.randint(1,5)}', f'WH-{random.randint(1,5)}')
        elif 'discrepancy' in template:
            return template.format(random.choice(PRODUCTS))
        else:
            return template.format(random.choice(ORDERS))
    elif service == 'order-service':
        order_id = random.choice(ORDERS)
        if 'created' in template:
            return template.format(order_id, random.choice(USERNAMES))
        elif 'status updated' in template:
            return template.format(order_id, random.choice(['processing', 'shipped', 'delivered', 'cancelled']))
        elif 'shipped' in template:
            return template.format(order_id, random.choice(['FedEx', 'UPS', 'USPS']), 
                                 f'1Z{random.randint(100000000,999999999)}')
        elif 'cancelled by' in template:
            return template.format(order_id, random.choice(USERNAMES))
        else:
            return template.format(order_id)
    elif service == 'search-service':
        if 'query executed' in template:
            return template.format(random.choice(SEARCH_QUERIES), random.randint(0, 500))
        elif 'index updated' in template:
            return template.format(random.randint(100, 10000))
        elif 'Autocomplete' in template or 'Zero results' in template:
            return template.format(random.choice(SEARCH_QUERIES))
        elif 'filter applied' in template:
            return template.format(random.choice(['price', 'category', 'brand']), random.choice(USERNAMES))
        elif 'Popular' in template:
            return template.format('last 7 days')
        elif 'relevance' in template or 'synonym' in template:
            return template.format(random.choice(['electronics', 'accessories', 'computers']))
        else:
            return template.format(random.choice(SEARCH_QUERIES), random.randint(50, 500))
    
    return template

def generate_logs(count=200):
    """Generate encrypted Kibana logs"""
    logs = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(count):
        # Generate timestamp
        timestamp = start_time + timedelta(seconds=random.randint(0, 86400))
        
        # Select service
        service = random.choice(list(SERVICES.keys()))
        
        # Generate message
        message = generate_message(service)
        
        # Select log level (weighted)
        level = random.choices(LOG_LEVELS, weights=LEVEL_WEIGHTS)[0]
        
        # Encrypt the message
        encrypted_message = encrypt_aes_cbc(message, KEY)
        
        # Create log entry
        log_entry = {
            "_index": random.choice(INDICES),
            "_id": f"log-{i+1:04d}",
            "_score": None,
            "_source": {
                "@timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "level": level,
                "service": service,
                "message": encrypted_message,
                "host": f"server-{random.randint(1,10)}",
                "environment": random.choice(["production", "staging"]),
                "request_id": f"req-{random.randint(100000,999999)}",
                "duration_ms": random.randint(10, 5000) if random.random() > 0.7 else None
            }
        }
        
        logs.append(log_entry)
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['_source']['@timestamp'])
    
    return logs

# Generate the logs
print("Generating 200 encrypted log entries...")
logs = generate_logs(200)

# Write to file
output_file = 'examples/kibana_logs_large.json'
with open(output_file, 'w') as f:
    json.dump(logs, f, indent=2)

print(f"✅ Generated {len(logs)} logs")
print(f"📝 Saved to: {output_file}")
print(f"📊 Services: {list(SERVICES.keys())}")
print(f"📈 Log levels distribution:")
for level in LOG_LEVELS:
    count = sum(1 for log in logs if log['_source']['level'] == level)
    print(f"   {level}: {count}")
