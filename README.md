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
