import asyncio
from config import TG_API_KEY,TG_API_HASH, TG_PHONE_NUMBER, CHAT_TARGETS, MAX_MESSAGES_PER_CHAT
from telethon import TelegramClient
import os

IMG_DIR = "./images"
DOC_DIR = "./documents"

async def fmt_msg_html(msg, chat_dict, tgc: TelegramClient, include_reply=True):
    _text = msg.text
    _from = (await msg.get_sender()).username
    _date = msg.date
    reply_to = None
    if include_reply:
        reply_to = msg.reply_to_msg_id
        _reply_txt = None
        if reply_to is not None:
            _reply = chat_dict[reply_to]
            _reply_txt = chat_dict[reply_to].text
            _reply_from = (await _reply.get_sender()).username

    _document = msg.document
    _photo = msg.photo

    if _document is not None:
        _filename = _document.attributes[0].file_name
        if not _filename:
            _filename = _document.id
        _save_path = os.path.join(DOC_DIR, _filename)
        doc_path = await tgc.download_media(_document, file=_save_path)
        doc_path= os.path.join(os.getcwd(), doc_path)

    if _photo is not None:
        _filename = str(_photo.id)
        _save_path = os.path.join(IMG_DIR, _filename)
        img_path = await tgc.download_media(_photo, file=_save_path)
        img_path = os.path.join(os.getcwd(), img_path)

    h_img = f"<img src='{img_path}'/>" if _photo is not None else ""
    h_from = f"<span class='from'>@{_from}</span>"
    h_time = f"<span class='time'>({_date})</span>"
    if reply_to is not None:
        h_quote = f"<span class='quote'><br>&nbsp;| {_reply_from}&nbsp;{_reply_txt}</span>"
    else:
        h_quote = ""
    if _document is not None:
        h_doc = f"<br><span class='doc'>&nbsp;<a href={doc_path}> attachment </a> </span>"
    else:
        h_doc = ""
    h_txt = f"<br><span class='text'>{_text}</span>"
    return f"<div class='msg'>{h_img}<p>{h_from}&nbsp;{h_time}{h_quote}{h_txt}{h_doc}</p></div>"

async def fmt_chat_html(chat_name, chat_dict, tgc: TelegramClient):
    header = f"<html><title>{chat_name}</title>"
    chat_html = "<style>img {max-height:250px; max-width:250px;} \
                .from {font-weight: bold;}\
                .msg {border-style: solid;border-width: 1px;}\
                .quote, .doc, .time {font-style: italic;}</style>"
    msges_html = ""
    for v in chat_dict.values():
        msges_html = msges_html + await fmt_msg_html(v, chat_dict, tgc)

    return header + chat_html + msges_html + "</html>"

async def main():
    global IMG_DIR, DOC_DIR
    # pull user configs from config.py or ask the user manually
    phone = TG_PHONE_NUMBER if TG_PHONE_NUMBER is not None else input("Enter your phone number: ")
    api_id = TG_API_KEY if TG_API_KEY is not None else input("Enter your api id: ")
    api_hash = TG_API_HASH if TG_API_HASH is not None else input("Enter your api hash: ")

    # log into telegram 
    tgc = TelegramClient('session', api_id, api_hash)
    await tgc.start(phone=lambda: phone)
    me = await tgc.get_me()
    print("Logged in as: " + me.username)
    
    # ask user for chats to archive, or pull from config.py if filled out
    if not CHAT_TARGETS:
        _prompt = "Enter chat name(s) to archive, comma-separated: "
        targets = [s.strip(' ').lower() for s in input(_prompt)]
    else:
        targets = CHAT_TARGETS

    # get all messages from chats
    chats = {}
    chat_ids = await tgc.get_dialogs()
    for chat in chat_ids:
        _chat_name = chat.name.lower()
        if _chat_name in targets:
            print("Found chat: " + chat.name)
            print("Getting messages...")
            msg_list = [msg for msg in await tgc.get_messages(_chat_name, MAX_MESSAGES_PER_CHAT)]
            msges = {}
            for msg in msg_list:
                msges[msg.id] = msg
            chats[_chat_name] = msges

    # fmt as html and save to directory with images and files
    for chat_name, chat_dict in chats.items():
        print("Formatting chat: " + chat_name)
        _name = chat_name.replace(' ', '_')
        if not os.path.exists(_name):
            os.mkdir(_name)
        IMG_DIR = os.path.join(_name, "images")
        DOC_DIR = os.path.join(_name, "documents")

        html = await fmt_chat_html(_name, chat_dict, tgc)
        # saves to ./chat_name/chat_name.html
        filename  = os.path.join(_name, _name + ".html")
        with open(filename, 'w') as f:
            f.write(html)
        print(f"Wrote chat: {_name} to file {filename}")

if __name__ == "__main__":
    asyncio.run(main())
