# tgfolder
Telegram cli for folder management

# Install
```bash
python3.8 -m venv venv
source venv/bin/activate
pip install .
```

# Configure
Go to https://my.telegram.org and create an application. Then create workdir:
```bash
mkdir ~/.tgfolder
```
Then create config file `~/.tgfolder/config.json` using the credentials:
```json
{"api_id": 111, "api_hash": "xxx", "phone": "+79999999999"}
```

# Run
```bash
tgfolder --help
tgfolder list
```

# Add all common chats
```bash
tgfolder include_peers list -t "ya target" | jq .id | xargs tgfolder common_chat_list | jq .id | xargs tgfolder include_peers add -t ya
```
