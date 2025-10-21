# pisync

## Deployment

```bash
pyinstaller --noconfirm --clean PiSync.spec
```

```bash
pyinstaller --noconfirm --onedir --windowed \
  -n "PiSync" \
  --icon="assets/icons/pisync_logo.png" \
  --add-data="assets/:assets" \
  --add-data="ui/:ui" \
  --add-data="src/:src" \
  main.py
```
