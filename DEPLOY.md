# Deployment Guide

## Dokploy Deployment

### Step 1: Prepare Repository

Make sure your repository is pushed to GitHub/GitLab/Bitbucket.

### Step 2: Create Application in Dokploy

1. Log in to your Dokploy instance
2. Create a new Application
3. Select "Docker" as deployment type
4. Connect your Git repository

### Step 3: Configure Environment Variables

In Dokploy settings, add the following environment variables:

**Required:**
- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather
- `GROQ_API_KEY` - Your Groq API key from console.groq.com

**Optional:**
- `ADMIN_USER_ID` - Your Telegram user ID
- `PROXY_URL` - Proxy URL if Groq is blocked (e.g., `http://proxy:port`)

### Step 4: Deploy

1. Dokploy will automatically detect `Dockerfile`
2. Click "Deploy" button
3. Monitor build logs
4. Once deployed, check application logs to ensure bot is running

### Step 5: Configure Bot

1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/mybots`
3. Select your bot
4. Go to **Bot Settings** → **Group Privacy** → **Turn off**
5. This allows the bot to read all messages in groups

## Docker Compose Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd goals_comment_bot

# Create environment file
cp .env.example .env
nano .env  # Edit with your values

# Start the bot
docker-compose up -d

# Check logs
docker-compose logs -f bot

# Stop the bot
docker-compose down
```

## Manual Docker Deployment

```bash
# Build image
docker build -t goals-comment-bot .

# Run container
docker run -d \
  --name goals-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/roles.json:/app/roles.json \
  goals-comment-bot

# View logs
docker logs -f goals-bot

# Stop container
docker stop goals-bot
docker rm goals-bot
```

## Persistent Data

The bot stores roles in `roles.json` file. Make sure to:
- Mount this file as a volume in Docker
- Back it up regularly
- Don't commit it to Git (already in `.gitignore`)

## Troubleshooting

### Bot shows "Conflict" error
- Another instance is running with the same token
- Stop all other instances
- Wait 30-60 seconds before starting again

### Bot doesn't respond in groups
- Check Privacy Mode is disabled in @BotFather
- Make sure bot is admin in the group (optional but recommended)

### LLM API errors
- Check your Groq API key is valid
- If Groq is blocked, configure `PROXY_URL`
- Check API rate limits

### Container keeps restarting
- Check logs: `docker logs goals-bot`
- Verify all required environment variables are set
- Check `.env` file format (no quotes around values)
