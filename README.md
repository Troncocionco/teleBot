# teleBot
Just playing around with Telegram's Bot APi

Need to install this python module first

```bash
sudo apt install python3-venv python3-full  # se non è già installato

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

```

- Get new 'Anteprima' from Panini.it based on the issue requested
- Filtering msg from a specific Telegram Channel
- Inline query towards Comicsbox.it 

Bot-Father command's description:
```
start - Initialize bot
ip - returns useful addresses
id - return user & chat id
uscite - returns latest release (opt. #week, #releases)
anteprima - last available on db
plex - clear and update plex server index
```

TO-do:
- Implement older feature with new library version
- Double-check presence of 'jq' utility on the system
- Fix service configuration file
- Implement logging feature

Credit: https://gist.github.com/ahmedsadman/2c1f118a02190c868b33c9c71835d706
