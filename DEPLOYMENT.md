# TTSAI Backend Deployment Guide

This guide walks you through deploying the TTSAI backend with SQLite database to Google Cloud Run.

## Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **Docker** installed and running
3. **GEMINI_API_KEY** environment variable set
4. **Google Cloud Project** with billing enabled

## Setup Google Cloud

1. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   gcloud config set project ttsai-461209
   ```

2. **Enable required APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

## Set Environment Variables

### Windows (Command Prompt/PowerShell):
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```

### Linux/Mac (Bash):
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

**For Windows:**
```cmd
deploy.bat
```

**For Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment

1. **Build and push Docker image:**
   ```bash
   gcloud builds submit --tag gcr.io/ttsai-461209/ttsai-backend:latest ./backend
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy ttsai-backend \
     --image gcr.io/ttsai-461209/ttsai-backend:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 5000 \
     --memory 1Gi \
     --cpu 1 \
     --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY,DATABASE_URL=sqlite:///app/ttsai.db"
   ```

## What Happens During Deployment

1. **Docker Build**: Creates container with SQLite support
2. **Database Migration**: Populates SQLite with initial data:
   - 38+ words for word-of-day feature
   - 32+ common phrases
   - Default user preferences
   - Analytics structure
3. **Cloud Run Deployment**: Deploys containerized backend
4. **Health Check**: Verifies service is running

## Verification Steps

After deployment, test the endpoints:

1. **Health Check:**
   ```bash
   curl https://ttsai-backend-321805997355.us-central1.run.app/api/health
   ```

2. **Word of Day:**
   ```bash
   curl "https://ttsai-backend-321805997355.us-central1.run.app/api/word-of-day?language=en"
   ```

3. **Supported Languages:**
   ```bash
   curl https://ttsai-backend-321805997355.us-central1.run.app/api/supported-languages
   ```

## Database Features Included

- ✅ **Word of Day**: Populated with vocabulary for multiple languages
- ✅ **Common Phrases**: Ready-to-use phrase collections
- ✅ **Flashcards**: SQLite-based spaced repetition system
- ✅ **User Progress**: Comprehensive progress tracking
- ✅ **Analytics**: Learning behavior tracking
- ✅ **Preferences**: User customization storage

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI translation features
- `DATABASE_URL`: SQLite database path (sqlite:///app/ttsai.db)
- `PORT`: Service port (5000)

### Resource Allocation
- **Memory**: 1GB RAM
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds
- **Max Instances**: Auto-scaling based on demand

## Troubleshooting

### Common Issues

1. **Build Fails**: Ensure Docker is running and you're authenticated to gcloud
2. **Migration Errors**: Check that data files exist in backend/data/
3. **Permission Denied**: Run `gcloud auth login` to re-authenticate
4. **API Key Missing**: Verify GEMINI_API_KEY environment variable is set

### Monitoring

View logs in real-time:
```bash
gcloud run logs tail ttsai-backend --region=us-central1
```

### Rollback

If issues occur, rollback to previous version:
```bash
gcloud run services replace-traffic ttsai-backend --to-revisions=PREVIOUS_REVISION=100 --region=us-central1
```

## Local Testing

Before deployment, test locally:

1. **Run migration:**
   ```bash
   cd backend
   python migrate_to_sqlite.py
   ```

2. **Test database:**
   ```bash
   python test_db.py
   ```

3. **Start local server:**
   ```bash
   python app.py
   ```

## Deployment Checklist

- [ ] Google Cloud CLI authenticated
- [ ] GEMINI_API_KEY environment variable set
- [ ] Required APIs enabled
- [ ] Local migration tested successfully
- [ ] Database tests passing
- [ ] Deploy script executed
- [ ] Health check endpoint responding
- [ ] Word-of-day endpoint returning data
- [ ] Frontend can connect to new backend

## Next Steps

After successful deployment:

1. Update frontend environment variables if needed
2. Test all application features
3. Monitor performance and logs
4. Set up automated backups for database (optional)

For support, check the logs and error messages during deployment. 