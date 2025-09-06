# Vercel Deployment Guide

This guide will help you deploy the n8n Workflow Popularity Tracker to Vercel.

## Prerequisites

1. A Vercel account (free tier is sufficient)
2. A YouTube Data API v3 key
3. Git repository with your code

## Quick Deployment

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**

   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**

   - Go to [vercel.com](https://vercel.com)
   - Sign in with your GitHub account
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Python project

3. **Configure Environment Variables**

   - In the Vercel dashboard, go to your project settings
   - Navigate to "Environment Variables"
   - Add the following variables:

   | Variable             | Value                       | Description                              |
   | -------------------- | --------------------------- | ---------------------------------------- |
   | `YOUTUBE_API_KEY`    | `your_youtube_api_key_here` | YouTube Data API v3 key (required)       |
   | `N8N_FORUM_API_KEY`  | `your_forum_api_key`        | n8n Forum API key (optional)             |
   | `N8N_FORUM_BASE_URL` | `https://community.n8n.io`  | n8n Forum base URL                       |
   | `DATABASE_URL`       | `sqlite:///:memory:`        | Database URL (auto-configured)           |
   | `DEBUG`              | `False`                     | Debug mode (set to False for production) |
   | `LOG_LEVEL`          | `INFO`                      | Logging level                            |

4. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete
   - Your API will be available at `https://your-project-name.vercel.app`

### Option 2: Deploy using Vercel CLI

1. **Install Vercel CLI**

   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**

   ```bash
   vercel login
   ```

3. **Deploy**

   ```bash
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add YOUTUBE_API_KEY
   vercel env add N8N_FORUM_API_KEY
   vercel env add N8N_FORUM_BASE_URL
   vercel env add DEBUG
   vercel env add LOG_LEVEL
   ```

## API Endpoints

Once deployed, your API will be available at:

- **Base URL**: `https://your-project-name.vercel.app`
- **API Documentation**: `https://your-project-name.vercel.app/docs`
- **Health Check**: `https://your-project-name.vercel.app/health`

### Main Endpoints

- `GET /workflows` - Get all workflows
- `GET /workflows/{platform}` - Get workflows by platform
- `GET /workflows/top/{n}` - Get top N workflows
- `GET /workflows/stats` - Get workflow statistics
- `POST /collect/all` - Collect data from all platforms

## Important Notes

### Database Limitations

- **In-Memory SQLite**: The current configuration uses in-memory SQLite for Vercel deployment
- **Data Persistence**: Data will be lost when the serverless function restarts
- **Production Recommendation**: For production use, consider:
  - PostgreSQL with Vercel Postgres
  - MongoDB Atlas
  - PlanetScale
  - Supabase

### Function Timeout

- **Default Timeout**: 30 seconds (configured in `vercel.json`)
- **Data Collection**: Background tasks may timeout for large data collection
- **Recommendation**: Use external services for heavy data processing

### API Rate Limits

- **YouTube API**: Respects YouTube API quotas
- **Vercel**: 100GB-hours per month on free tier
- **Recommendation**: Implement caching and rate limiting

## Environment Variables Reference

### Required Variables

| Variable          | Description             | Example                                   |
| ----------------- | ----------------------- | ----------------------------------------- |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIzaSyBEaKtU5aB2DiIQT2f_svHCIkdBQOBaq6k` |

### Optional Variables

| Variable                 | Description                    | Default                                                   |
| ------------------------ | ------------------------------ | --------------------------------------------------------- |
| `N8N_FORUM_API_KEY`      | n8n Forum API key              | `""`                                                      |
| `N8N_FORUM_BASE_URL`     | n8n Forum base URL             | `https://community.n8n.io`                                |
| `DATABASE_URL`           | Database connection string     | `sqlite:///:memory:`                                      |
| `DEBUG`                  | Enable debug mode              | `False`                                                   |
| `LOG_LEVEL`              | Logging level                  | `INFO`                                                    |
| `YOUTUBE_SEARCH_QUERIES` | Comma-separated search queries | `n8n workflow,n8n automation,n8n integration`             |
| `TRENDS_QUERIES`         | Comma-separated trend queries  | `n8n Slack integration,n8n Gmail automation,n8n workflow` |
| `TRENDS_COUNTRIES`       | Comma-separated country codes  | `US,IN`                                                   |

## Testing Your Deployment

1. **Health Check**

   ```bash
   curl https://your-project-name.vercel.app/health
   ```

2. **Get Workflows**

   ```bash
   curl https://your-project-name.vercel.app/workflows
   ```

3. **API Documentation**
   Visit: `https://your-project-name.vercel.app/docs`

## Troubleshooting

### Common Issues

1. **Import Errors**

   - Ensure all dependencies are in `api/requirements.txt`
   - Check that Python path is correctly set in `api/index.py`

2. **Database Errors**

   - Verify database URL is set correctly
   - Check that tables are created on startup

3. **API Key Issues**

   - Verify YouTube API key is valid
   - Check API quotas and limits

4. **Timeout Errors**
   - Reduce data collection size
   - Implement async processing
   - Use external services for heavy tasks

### Debug Mode

To enable debug mode:

1. Set `DEBUG=True` in environment variables
2. Check Vercel function logs
3. Use the `/health` endpoint for basic connectivity

## Production Recommendations

1. **Database**: Use a persistent database service
2. **Caching**: Implement Redis or similar for caching
3. **Monitoring**: Set up error tracking and monitoring
4. **Rate Limiting**: Implement proper rate limiting
5. **Security**: Add authentication and authorization
6. **Backup**: Regular data backups and disaster recovery

## Support

For issues with deployment:

1. Check Vercel function logs
2. Verify environment variables
3. Test locally with `vercel dev`
4. Check API documentation at `/docs`

## Cost Considerations

- **Free Tier**: 100GB-hours per month
- **Pro Tier**: $20/month for unlimited usage
- **Database**: Consider external database costs
- **API Calls**: Monitor YouTube API usage

## Next Steps

1. Set up a persistent database
2. Implement proper error handling
3. Add authentication
4. Set up monitoring and alerts
5. Implement caching strategies
6. Add comprehensive testing
