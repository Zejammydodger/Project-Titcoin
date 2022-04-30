import asyncio


# cooldown async function
async def cooldownFunc(userID : int, cooldownTime:int, cooldown: list[int]):
    cooldown.append(userID)
    await asyncio.sleep(cooldownTime)
    cooldown.pop(cooldown.index(userID))