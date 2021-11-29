# https://github.com/1Danish-00/CompressorQueue/blob/main/License> .


import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import asyncio
import os
import time
import re
import json
import subprocess
import math

from .FastTelethon import download_file, upload_file
from .funcn import *
from .config import *

pid_list = []

async def stats(e):
    try:
        wah = e.pattern_match.group(1).decode("UTF-8")
        wh = decode(wah)
        out, dl, id = wh.split(";")
        ot = hbs(int(Path(out).stat().st_size))
        ov = hbs(int(Path(dl).stat().st_size))
        processing_file_name = dl.replace(f"downloads/", "").replace(f"_", " ")
        ans = f"Processing Media:\n{processing_file_name}\n\nDownloaded:\n{ov}\n\nCompressed:\n{ot}\n\nTime Left:\n{ETA}\n\nProcessed:\n{percentage}'"
        await e.answer(ans, cache_time=0, alert=True)
    except Exception as er:
        LOGS.info(er)
        await e.answer(
            "Someting Went Wrong.\nSend Media Again.", cache_time=0, alert=True
        )


async def dl_link(event):
    if not event.is_private:
        return
    if str(event.sender_id) not in OWNER and event.sender_id !=DEV:
        return
    link, name = "", ""
    try:
        link = event.text.split()[1]
        name = event.text.split()[2]
    except BaseException:
        pass
    if not link:
        return
    if WORKING or QUEUE:
        QUEUE.update({link: name})
        return await event.reply(f"**✅ Added {link} in QUEUE**")
    WORKING.append(1)
    s = dt.now()
    xxx = await event.reply("**📥 Downloading...**")
    try:
        dl = await fast_download(xxx, link, name)
    except Exception as er:
        WORKING.clear()
        LOGS.info(er)
        return
    es = dt.now()
    kk = dl.split("/")[-1]
    aa = kk.split(".")[-1]
    newFile = dl.replace(f"downloads/", "").replace(f"_", " ")
    rr = "encode"
    bb = kk.replace(f".{aa}", " [CBZ].mkv")
    out = f"{rr}/{bb}"
    thum = "thumb.jpg"
    dtime = ts(int((es - s).seconds) * 1000)
    hehe = f"{out};{dl};0"
    wah = code(hehe)
    nn = await xxx.edit(
        "**🗜 Compressing...**",
        buttons=[
            [Button.inline("STATS", data=f"stats{wah}")],
            [Button.inline("CANCEL", data=f"skip{wah}")],
        ],
    )
    cmd = f"""ffmpeg -i "{dl}" {ffmpegcode[0]} "{out}" -y"""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    er = stderr.decode()


    progress = "downloads" + "/" + "progress.txt"
    with open(progress, 'w') as f:
      pass
    COMPRESSION_START_TIME = time.time()    
    LOGGER.info("ffmpeg_process: "+str(process.pid))
    pid_list.insert(0, process.pid)
    status = "downloads" + "/status.json"
    with open(status, 'r+') as f:
      statusMsg = json.load(f)
      statusMsg['pid'] = process.pid
      statusMsg['e'] = e.chat_id
      f.seek(0)
      json.dump(statusMsg,f,indent=2)
    isDone = False
    while process.returncode != 0:
      await asyncio.sleep(3)
      with open("downloads" + "/progress.txt", 'r+') as file:
        text = file.read()
        frame = re.findall("frame=(\d+)", text)
        time_in_us=re.findall("out_time_ms=(\d+)", text)
        progress=re.findall("progress=(\w+)", text)
        speed=re.findall("speed=(\d+\.?\d*)", text)
        if len(frame):
          frame = int(frame[-1])
        else:
          frame = 1;
        if len(speed):
          speed = speed[-1]
        else:
          speed = 1;
        if len(time_in_us):
          time_in_us = time_in_us[-1]
        else:
          time_in_us = 1;
        if len(progress):
          if progress[-1] == "end":
            LOGGER.info(progress[-1])
            isDone = True
            break
        execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME)*1000)
        elapsed_time = int(time_in_us)/1000000
        difference = math.floor( (total_time - elapsed_time) / float(speed) )
        ETA = "-"
        if difference > 0:
          ETA = TimeFormatter(difference*1000)
        percentage = math.floor(elapsed_time * 100 / total_time)
        
    try:
        if er:
            await xxx.edit(str(er) + "\n\n**ERROR**")
            WORKING.clear()
            os.remove(dl)
            return os.remove(out)
    except BaseException:
        pass
    ees = dt.now()
    ttt = time.time()
    await nn.delete()
    nnn = await xxx.client.send_message(xxx.chat_id, "**📤 Uploading...**")
    with open(out, "rb") as f:
        ok = await upload_file(
            client=xxx.client,
            file=f,
            name=out,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, nnn, ttt, "**📤 Uploading...**")
            ),
        )
    await nnn.delete()
    org = int(Path(dl).stat().st_size)
    com = int(Path(out).stat().st_size)
    pe = 100 - ((com / org) * 100)
    per = str(f"{pe:.2f}") + "%"
    eees = dt.now()
    x = dtime
    xx = ts(int((ees - es).seconds) * 1000)
    xxx = ts(int((eees - ees).seconds) * 1000)
    a1 = await info(dl, xxx)
    a2 = await info(out, xxx)
    dk = f"<b>File Name:</b> {newFile}\n\n<b>Original File Size:</b> {hbs(org)}\n<b>Encoded File Size:</b> {hbs(com)}\n<b>Encoded Percentage:</b> {per}\n\n<b>Get Mediainfo here:</b> <a href='{a1}'>Before</a>/<a href='{a2}'>After</a>\n\n<i>Downloaded in {x}\nEncoded in {xx}\nUploaded in {xxx}</i>"
    ds = await e.client.send_file(
        e.chat_id, file=ok, force_document=True, caption=dk, link_preview=False, thumb=thum, parse_mode="html"
    )
    os.remove(dl)
    os.remove(out)
    WORKING.clear()





async def encod(event):
    try:
        if not event.is_private:
            return
        event.sender
        if str(event.sender_id) not in OWNER and event.sender_id !=DEV:
            return await event.reply("**Sorry You're not An Authorised User!**")
        if not event.media:
            return
        if hasattr(event.media, "document"):
            if not event.media.document.mime_type.startswith(
                ("video", "application/octet-stream")
            ):
                return
        else:
            return
        if WORKING or QUEUE:
            xxx = await event.reply("**Adding To Queue...**")
            # id = pack_bot_file_id(event.media)
            doc = event.media.document
            if doc.id in list(QUEUE.keys()):
                return await xxx.edit("**This File is Already Added in Queue**")
            name = event.file.name
            if not name:
                name = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
            QUEUE.update({doc.id: [name, doc]})
            return await xxx.edit(
                "**Added This File in Queue**"
            )
        WORKING.append(1)
        xxx = await event.reply("**📥 Downloading...**")
        s = dt.now()
        ttt = time.time()
        dir = f"downloads/"
        try:
            if hasattr(event.media, "document"):
                file = event.media.document
                filename = event.file.name
                if not filename:
                    filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
                dl = dir + filename
                with open(dl, "wb") as f:
                    ok = await download_file(
                        client=event.client,
                        location=file,
                        out=f,
                        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                            progress(
                                d,
                                t,
                                xxx,
                                ttt,
                                "**📥 Downloading...**",
                            )
                        ),
                    )
            else:
                dl = await event.client.download_media(
                    event.media,
                    dir,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, xxx, ttt, "**📥 Downloading...**")
                    ),
                )
        except Exception as er:
            WORKING.clear()
            LOGS.info(er)
            return os.remove(dl)
        es = dt.now()
        kk = dl.split("/")[-1]
        aa = kk.split(".")[-1]
        rr = f"encode"
        bb = kk.replace(f".{aa}", " [CBZ].mkv")
        newFile = dl.replace(f"downloads/", "").replace(f"_", " ")
        out = f"{rr}/{bb}"
        thum = "thumb.jpg"
        dtime = ts(int((es - s).seconds) * 1000)
        e = xxx
        hehe = f"{out};{dl};0"
        wah = code(hehe)
        nn = await e.edit(
            "**🗜 Compressing...**",
            buttons=[
                [Button.inline("STATS", data=f"stats{wah}")],
                [Button.inline("CANCEL", data=f"skip{wah}")],
            ],
        )
        cmd = f"""ffmpeg -i "{dl}" {ffmpegcode[0]} "{out}" -y"""
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        er = stderr.decode()
        progress = "downloads" + "/" + "progress.txt"
       with open(progress, 'w') as f:
         pass
       COMPRESSION_START_TIME = time.time()    
       LOGGER.info("ffmpeg_process: "+str(process.pid))
       pid_list.insert(0, process.pid)
       status = "downloads" + "/status.json"
       with open(status, 'r+') as f:
         statusMsg = json.load(f)
         statusMsg['pid'] = process.pid
         statusMsg['e'] = e.chat_id
         f.seek(0)
         json.dump(statusMsg,f,indent=2)
       isDone = False
       while process.returncode != 0:
         await asyncio.sleep(3)
         with open("downloads" + "/progress.txt", 'r+') as file:
           text = file.read()
           frame = re.findall("frame=(\d+)", text)
           time_in_us=re.findall("out_time_ms=(\d+)", text)
           progress=re.findall("progress=(\w+)", text)
           speed=re.findall("speed=(\d+\.?\d*)", text)
           if len(frame):
             frame = int(frame[-1])
           else:
             frame = 1;
           if len(speed):
             speed = speed[-1]
           else:
             speed = 1;
           if len(time_in_us):
             time_in_us = time_in_us[-1]
           else:
             time_in_us = 1;
           if len(progress):
             if progress[-1] == "end":
               LOGGER.info(progress[-1])
               isDone = True
               break
           execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME)*1000)
           elapsed_time = int(time_in_us)/1000000
           difference = math.floor( (total_time - elapsed_time) / float(speed) )
           ETA = "-"
           if difference > 0:
             ETA = TimeFormatter(difference*1000)
           percentage = math.floor(elapsed_time * 100 / total_time)
        try:
            if er:
                await e.edit(str(er) + "\n\n**ERROR**")
                WORKING.clear()
                os.remove(dl)
                return os.remove(out)
        except BaseException:
            pass
        ees = dt.now()
        ttt = time.time()
        await nn.delete()
        nnn = await e.client.send_message(e.chat_id, "**📤 Uploading...**")
        with open(out, "rb") as f:
            ok = await upload_file(
                client=e.client,
                file=f,
                name=out,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, nnn, ttt, "**📤 Uploading...**")
                ),
            )
        await nnn.delete()
        org = int(Path(dl).stat().st_size)
        com = int(Path(out).stat().st_size)
        pe = 100 - ((com / org) * 100)
        per = str(f"{pe:.2f}") + "%"
        eees = dt.now()
        x = dtime
        xx = ts(int((ees - es).seconds) * 1000)
        xxx = ts(int((eees - ees).seconds) * 1000)
        a1 = await info(dl, e)
        a2 = await info(out, e)
        dk = f"<b>File Name:</b> {newFile}\n\n<b>Original File Size:</b> {hbs(org)}\n<b>Encoded File Size:</b> {hbs(com)}\n<b>Encoded Percentage:</b> {per}\n\n<b>Get Mediainfo here:</b> <a href='{a1}'>Before</a>/<a href='{a2}'>After</a>\n\n<i>Downloaded in {x}\nEncoded in {xx}\nUploaded in {xxx}</i>"
        ds = await e.client.send_file(
            e.chat_id, file=ok, force_document=True, caption=dk, link_preview=False, thumb=thum, parse_mode="html"
        )
        os.remove(dl)
        os.remove(out)
        WORKING.clear()
    except BaseException as er:
        LOGS.info(er)
        WORKING.clear()
