# How to Use the Decrypt & Download Feature

## 🎯 Quick Start

### Step 1: Access the Application
Navigate to: http://localhost:8080

### Step 2: Login
- Username: `admin`
- Password: `admin`

### Step 3: Choose Your Method

## 📁 Method 1: File Upload with Download

### A. Decrypt & View (Display in Browser)
1. Click **"📁 File Upload"** tab
2. Select file: `examples/kibana_logs_elasticsearch.json`
3. Enter encryption key or upload key file
4. Click **"🔓 Decrypt & View"** button
5. Results appear on the page with diff view

### B. Decrypt & Download (Save to File)
1. Click **"📁 File Upload"** tab
2. Select file: `examples/kibana_logs_elasticsearch.json`
3. Enter encryption key or upload key file
4. Click **"💾 Decrypt & Download"** button
5. File automatically downloads as JSON

**Downloaded Filename Format:**
```
decrypted_logs_abc123_2026-02-02.json
```

## 🔍 Method 2: Kibana with Download

### A. Decrypt & View
1. Click **"🔌 Kibana"** tab
2. Enter Elasticsearch URL
3. Enter index name
4. Enter encryption key or upload key file
5. Configure optional settings
6. Click **"🔓 Decrypt & View"** button
7. Results appear on the page

### B. Decrypt & Download
1. Click **"🔌 Kibana"** tab
2. Enter all required information
3. Click **"💾 Decrypt & Download"** button
4. Wait for processing
5. File automatically downloads

## 📊 Downloaded File Format

The downloaded JSON file contains all decrypted logs:

```json
[
  {
    "_index": "logs-2026.02.02",
    "_type": "_doc",
    "_id": "1",
    "_source": {
      "@timestamp": "2026-02-02T20:30:00.000Z",
      "level": "INFO",
      "service": "user-service",
      "encrypted_message": "AES:BASE64:iv:encrypted_data",
      "decrypted_message": "User john.doe logged in successfully",
      "user": "john.doe"
    }
  },
  {
    "_index": "logs-2026.02.02",
    "_type": "_doc",
    "_id": "2",
    "_source": {
      "@timestamp": "2026-02-02T20:31:00.000Z",
      "level": "WARN",
      "service": "payment-service",
      "encrypted_message": "AES:BASE64:iv:encrypted_data",
      "decrypted_message": "Payment processing delayed for transaction tx_456",
      "transaction_id": "tx_456"
    }
  }
]
```

## 🎨 Button Differences

### 🔓 Decrypt & View (Green Button)
- **Purpose**: Display logs in the browser
- **Best For**: 
  - Quick inspection
  - Visual comparison of encrypted vs decrypted
  - Small log sets
  - Real-time analysis

### 💾 Decrypt & Download (Blue Button)
- **Purpose**: Save decrypted logs as a file
- **Best For**:
  - Large log sets
  - Offline analysis
  - Sharing with team members
  - Long-term storage
  - Further processing in other tools

## ⚙️ Processing Flow

### View Mode
```
Upload → Process → Display in Browser → Done
```

### Download Mode
```
Upload → Process → Download File → Save to Disk
```

## 📁 File Management

### Where Downloads Go
Files are saved to your browser's default download location:
- **Mac**: `~/Downloads/`
- **Windows**: `C:\Users\YourName\Downloads\`
- **Linux**: `~/Downloads/`

### File Naming Convention
```
decrypted_logs_{jobId}_{date}.json

Examples:
decrypted_logs_abc123_2026-02-02.json
decrypted_logs_def456_2026-02-02.json
```

## 🔍 Status Messages

### Processing States

#### ⏳ Uploading and processing for download...
- File is being uploaded
- Decryption job is being created
- Wait for next status

#### ⏳ Job {jobId} processing... Preparing download...
- Job is running on the server
- Decryption in progress
- Polling for completion

#### ✅ Decryption completed! Downloading...
- Job finished successfully
- File download is starting
- Check your downloads folder

#### ❌ Error: {message}
- Something went wrong
- Read the error message
- Check your inputs and try again

## 💡 Tips & Best Practices

### For Viewing
- ✅ Use for quick checks (< 100 logs)
- ✅ Use when you need the diff view
- ✅ Use for immediate analysis
- ✅ Use when you want to see timestamps and levels

### For Downloading
- ✅ Use for large datasets (> 100 logs)
- ✅ Use when you need offline access
- ✅ Use for archival purposes
- ✅ Use when sharing with others
- ✅ Use for processing in other tools (Excel, Python, etc.)

### Performance Tips
1. **Large Files**: Always use download mode for files > 10MB
2. **Slow Networks**: Download mode is more reliable
3. **Multiple Jobs**: Use download mode to avoid browser memory issues
4. **Long-term Storage**: Downloaded files can be backed up

## 🛠️ Troubleshooting

### Download Doesn't Start
1. Check browser console (F12) for errors
2. Verify job completed (check status message)
3. Ensure pop-up blocker is disabled
4. Try a different browser

### File is Empty
1. Check encryption key is correct
2. Verify log file has encrypted data
3. Check API logs: `docker-compose logs api`

### Download Fails Midway
1. Check disk space
2. Verify network connection
3. Try smaller log set first
4. Check browser download settings

### Wrong File Format
- Downloaded file is always JSON
- Pretty-printed with 2-space indentation
- Can be opened in any text editor
- Can be imported into Excel/Google Sheets

## 📊 Example Workflow

### Scenario: Daily Log Analysis

**Morning Routine:**
```
1. Open LogGin Genie
2. Upload yesterday's logs
3. Click "💾 Decrypt & Download"
4. Wait for download
5. Open in Excel/Python for analysis
```

**Quick Check:**
```
1. Open LogGin Genie
2. Upload specific log file
3. Click "🔓 Decrypt & View"
4. Scan through diff view
5. Look for errors/warnings
```

**Team Sharing:**
```
1. Decrypt logs with download
2. Save to shared folder
3. Team members access decrypted file
4. No need to share encryption keys
```

## 🎯 Advanced Usage

### Combining Both Modes
1. Use **View** first to verify decryption is working
2. Then use **Download** to save the full dataset
3. Analyze downloaded file in your preferred tool

### Batch Processing
1. Process multiple files sequentially
2. Each generates a unique filename
3. All files saved to downloads folder
4. Easy to organize by date/job ID

### Integration with Other Tools
```bash
# Python analysis
import json

with open('decrypted_logs_abc123_2026-02-02.json') as f:
    logs = json.load(f)
    
# Analyze logs
for log in logs:
    if log['_source']['level'] == 'ERROR':
        print(log['_source']['decrypted_message'])
```

---

**Happy Decrypting!** 🔓💾✨

For more information, see:
- `QUICKSTART.md` - Getting started guide
- `UI_IMPROVEMENTS.md` - Full feature list
- `UPDATES_SUMMARY.md` - Recent changes
