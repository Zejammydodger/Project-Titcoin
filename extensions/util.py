
### cooldown async function

async def cooldownFunc(userID : int, cooldown: list[int]):
    cooldown.append(userID)
    await asyncio.sleep(cooldownTime)
    cooldown.pop(cooldown.index(userID))