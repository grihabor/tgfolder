# tgfolder
Telegram cli for folder management

# Install
```bash
python3.8 -m venv venv
source venv/bin/activate
pip install .
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
