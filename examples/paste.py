from pastypy import Paste

paste = Paste(content="This is a paste from pastypy")
token = paste.save()

# Token isn't required if you created a new paste with `Paste.save()`
paste.edit(content="I needed to edit this paste", token=token)

other = Paste.get(id="abcdef123")
print(paste.content)
