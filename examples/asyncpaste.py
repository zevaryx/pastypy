from pastypy import AsyncPaste

paste = AsyncPaste(content="This is a paste from pastypy")
token = await paste.save()

# Token isn't required if you created a new paste with `Paste.save()`
await paste.edit(content="I needed to edit this paste", token=token)

other = await AsyncPaste.get(id="abcdef123")
print(paste.content)
