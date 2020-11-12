<div align="center">
    <img src="logo.png" alt="logo">
    <p>CLI alarm manager based on unix sockets</p>
</div>

---

```
python -m pip install alarmix
```

## Usage
⚠️ [MPV](https://mpv.io/) must be installed and accessible ⚠️
1. Start alarmd daemon
```bash
alarmd --sound "path/to/sound"
```

Then you can manage your alarms with `alarmc` command.
```bash
alarmc # Show scheduled alarms
alarmc stop # Stop buzzing alarm
alarmc add 20:00 19:30 14:00 # Add alarms
alarmc add 20:00 --delete # delete TODO: make other command
alarmc

alarmc -h # Show help
```