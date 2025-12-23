# Goals Comment Bot

Telegram 1>B =0 aiogram 3, :>B>@K9 :><<5=B8@C5B A>>1I5=8O 2 3@C??>2KE G0B0E 8A?>;L7CO 15A?;0B=>5 LLM API (Groq).

## >7<>6=>AB8

- 2B><0B8G5A:>5 :><<5=B8@>20=85 A>>1I5=89 2 3@C??>2KE G0B0E
- 0AB@08205<0O @>;L 1>B0 4;O :064>3> G0B0
- A?>;L7C5B Groq API A <>45;LN Llama 3.3 70B (15A?;0B=>)
- @>AB>5 C?@02;5=85 G5@57 :><0=4K Telegram

## #AB0=>2:0

1. ;>=8@C9B5 @5?>78B>@89
2. #AB0=>28B5 7028A8<>AB8:
```bash
uv sync
```

3. !>7409B5 `.env` D09; =0 >A=>25 `.env.example`:
```bash
cp .env.example .env
```

4. >;CG8B5 =5>1E>48<K5 API :;NG8:
   - **Telegram Bot Token**: A>7409B5 1>B0 G5@57 [@BotFather](https://t.me/BotFather)
   - **Groq API Key**: 70@538AB@8@C9B5AL =0 [console.groq.com](https://console.groq.com) 8 ?>;CG8B5 15A?;0B=K9 API :;NG

5. 0?>;=8B5 `.env` D09; 20H8<8 40==K<8

## 0?CA:

```bash
python main.py
# 8;8
uv run main.py
```

## A?>;L7>20=85

### ><0=4K 1>B0

- `/start` - 8=D>@<0F8O > 1>B5 8 4>ABC?=KE :><0=40E
- `/setrole <B5:AB>` - CAB0=>28BL @>;L 4;O 1>B0 2 B5:CI5< G0B5
- `/getrole` - ?>A<>B@5BL B5:CICN @>;L
- `/deleterole` - C40;8BL ?>;L7>20B5;LA:CN @>;L (25@=CBLAO : AB0=40@B=>9)

### @8<5@ CAB0=>2:8 @>;8

```
/setrole "K >?KB=K9 ?A8E>;>3-<>B820B>@. "2>O 7040G0 - 4020BL ?>445@6820NI85 8 <>B828@CNI85 :><<5=B0@88 : F5;O< ;N459. C4L M<?0B8G=K< 8 24>E=>2;ONI8<.
```

### >102;5=85 2 3@C??C

1. >102LB5 1>B0 2 20HC 3@C??C
2. 09B5 1>BC ?@020 =0 GB5=85 A>>1I5=89 (>B:;NG8B5 Privacy Mode 2 =0AB@>9:0E 1>B0 G5@57 @BotFather)
3. A?>;L7C9B5 `/setrole` GB>1K =0AB@>8BL ?>2545=85 1>B0
4. >B 1C45B 02B><0B8G5A:8 :><<5=B8@>20BL A>>1I5=8O 2 3@C??5

## !B@C:BC@0 ?@>5:B0

- `main.py` - B>G:0 2E>40, 70?CA: 1>B0
- `config.py` - :>=D83C@0F8O G5@57 Pydantic Settings
- `handlers.py` - >1@01>BG8:8 :><0=4 8 A>>1I5=89
- `llm_client.py` - :;85=B 4;O Groq API
- `database.py` - E@0=8;8I5 @>;59 (JSON)
- `roles.json` - D09; A A>E@0=5==K<8 @>;O<8 (A>7405BAO 02B><0B8G5A:8)

## "5E=>;>388

- Python 3.13+
- aiogram 3.x - Telegram Bot framework
- Groq API - 15A?;0B=>5 LLM API (Llama 3.3 70B)
- Pydantic - 20;840F8O :>=D83C@0F88
- aiohttp - 0A8=E@>==K5 HTTP 70?@>AK

## Configuration Options / Параметры конфигурации

### Bot-Specific Settings

You can enable/disable features for each bot individually using comma-separated values:

#### Enable Chat History (`BOT_ENABLE_HISTORY`)
Controls whether the bot remembers previous messages in the conversation.
- Default: `false` (disabled)
- Example for 4 bots: `BOT_ENABLE_HISTORY=true,false,true,false`
  - Bot 1 & 3: Will remember chat history (up to `CHAT_HISTORY_LIMIT` messages)
  - Bot 2 & 4: No memory, each message is independent

#### Use Reply Mode (`BOT_USE_REPLY`)
Controls whether the bot uses reply (quotes the message) or just sends a regular message.
- Default: `false` (uses `answer` - regular message)
- Example for 4 bots: `BOT_USE_REPLY=false,true,false,true`
  - Bot 1 & 3: Regular messages (answer)
  - Bot 2 & 4: Reply with quote (reply)

#### Delete Previous Messages (`BOT_DELETE_PREVIOUS`)
Controls whether the bot deletes its previous message before sending a new one.
- Default: `true` (deletes previous messages)
- Example for 4 bots: `BOT_DELETE_PREVIOUS=true,false,true,false`
  - Bot 1 & 3: Will delete previous bot messages
  - Bot 2 & 4: Will keep all messages (history accumulates)

#### Channel Filter (`BOT_CHANNEL_IDS`)
Controls which channel the bot responds to (useful for discussion groups attached to channels).
- Default: `none` (responds to all messages)
- When set, bot will ONLY respond to messages from the specified channel
- Example for 4 bots: `BOT_CHANNEL_IDS=-1001234567890,none,-1009876543210,none`
  - Bot 1: Only responds to channel -1001234567890
  - Bot 2: Responds to all messages
  - Bot 3: Only responds to channel -1009876543210
  - Bot 4: Responds to all messages
- **How to get channel ID**: Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)

#### Example .env for 3 bots:
```env
BOT_TOKENS=TOKEN1,TOKEN2,TOKEN3
BOT_NAMES=Motivator,Psychologist,Coach
BOT_ENABLE_HISTORY=true,true,false
BOT_USE_REPLY=true,false,true
BOT_DELETE_PREVIOUS=true,false,true
BOT_CHANNEL_IDS=-1001234567890,none,none
CHAT_HISTORY_LIMIT=20
```

This configuration means:
- **Motivator**: History enabled, uses reply, deletes previous messages, only responds to channel -1001234567890
- **Psychologist**: History enabled, uses answer, keeps all messages, responds to all messages
- **Coach**: No history, uses reply, deletes previous messages, responds to all messages

## Deployment / Деплой

### Deploy with Dokploy

1. Create a new project in Dokploy
2. Connect your Git repository
3. Add environment variables in Dokploy settings:
   - `BOT_TOKENS` (comma-separated for multiple bots)
   - `GROQ_API_KEY`
   - `BOT_NAMES` (optional, comma-separated)
   - `BOT_ENABLE_HISTORY` (optional, comma-separated true/false)
   - `BOT_USE_REPLY` (optional, comma-separated true/false)
   - `BOT_DELETE_PREVIOUS` (optional, comma-separated true/false, default: true)
   - `BOT_CHANNEL_IDS` (optional, comma-separated channel IDs or "none", default: none)
   - `ADMIN_USER_IDS` (optional)
   - `PROXY_URL` (optional)
   - `CHAT_HISTORY_LIMIT` (optional, default: 20)
4. Dokploy will automatically detect `Dockerfile` and deploy

### Deploy with Docker Compose

```bash
# Create .env file
cp .env.example .env
# Edit .env with your values

# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Local Docker Build

```bash
# Build image
docker build -t goals-comment-bot .

# Run with .env file
docker run -d --env-file .env --name bot goals-comment-bot

# View logs
docker logs -f bot
```
