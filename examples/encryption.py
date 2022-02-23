from pastypy import Paste

paste = Paste(content="I am secret!")

# Encrypts the paste and gives you the key
key = paste.encrypt()
pid = paste.save()

# Get the paste later
paste = Paste.get(pid)

# Prints <Encrypted: encrypted_text>
print(paste.content)

# Prints "I am secret!"
paste.decrypt(key)
print(paste.content)
