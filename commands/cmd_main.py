

async def cmd_echo(*args):
  dis = args[0]
  user = args[0].author
  msg = " ".join(args[1:][0])
  reply = msg
  if len(msg) < 1:
    reply = "Ауууу"

  await dis.channel.send(reply)
