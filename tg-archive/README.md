
# a cli util for archiving telegram chats
usage:
0. set up your api keys at https://my.telegram.org/
1. configure `config.py` to your liking or ignore it and the program will guide you through connecting your telegram account
2. install the telethon telegram package: `python3 -m pip install --upgrade telethon`
3. run the script: `python main.py`
4. if you saved a chat named: `alfa groupchat 123`, open the newly created folder called`alfa_groupchat_123` and click on `alfa_groupchat_123.html` to view your archived chat.
5. send all of your ethereum to `0xAf8458844e817F11a139d0cC3Ab0454fd49c6d78`


# making changes
you can obviously play with the internals locally if you want, the source should be semi-readable. 
PRs are welcome/appreciated if you want to help make this more useful.

a few things that would be nice:
- only download chats in an arbitrary date range 
- nicer html formatting / maybe html templating
- save to CSV
- support for other types of media
- better error handling/less spaghetti




