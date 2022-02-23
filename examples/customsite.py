from pastypy import Paste

paste = Paste(content="This goes to a custom site!")
token = paste.save(site="https://pasty.example.com")

# Prints https://pasty.example.com/paste_id
print(paste.url)
