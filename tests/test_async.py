from datetime import datetime

import pytest

from pastypy import AsyncPaste

TEST_SITE = "https://paste.zevs.me"


def get_content(test_name):
    return f"---\nTest: {test_name}\nTime: {datetime.utcnow().timestamp()}"


def create_paste(test_name):
    return AsyncPaste(content=get_content(test_name), site=TEST_SITE)


def test_create():
    """Test creating a paste."""
    p = create_paste("test_create")
    assert p.id is None


def test_repr():
    """Test paste.__repr__."""
    p = AsyncPaste(content="test_repr")
    assert p.__repr__() == "<AsyncPaste: content=test_repr, encrypted=False>"


def test_content():
    """Test content."""
    content = "test_content"
    p = AsyncPaste(content=content)
    assert content == p.content
    _ = p.encrypt()
    p._plaintext = None
    assert p.content == f"<Encrypted: {p._content}>"


@pytest.mark.asyncio
async def test_save_delete():
    """Test saving and deleting a paste."""
    p = create_paste("test_save")
    with pytest.raises(ValueError):
        await p.delete()
    token = await p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token
    assert p.url == f"{TEST_SITE}/{p.id}"
    p._token = None
    with pytest.raises(ValueError):
        await p.delete()
    await p.delete(token)


@pytest.mark.asyncio
async def test_edit():
    """Test editing a paste."""
    p = create_paste("test_edit")
    with pytest.raises(ValueError):
        await p.edit(content="NI")
    content = p.content
    token = await p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token

    await p.edit(get_content("test_edit_post"))
    assert p.content != content
    p._token = None
    with pytest.raises(ValueError):
        await p.edit(content="NI")
    await p.delete(token)


@pytest.mark.asyncio
async def test_edit_enc():
    """Test editing an encrypted paste."""
    p = create_paste("test_edit_enc")
    key = p.encrypt()
    md = p.metadata
    await p.save()

    new_key = await p.edit(content="test_edit_enc_post")
    new_md = p.metadata
    assert key != new_key
    assert md != new_md
    await p.delete()


@pytest.mark.asyncio
async def test_get():
    """Test getting a paste."""
    p = create_paste("test_get")
    token = await p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token

    p2 = await AsyncPaste.get(p.id, site=TEST_SITE)
    assert p.id == p2.id
    assert p.content == p2.content
    await p.delete()


def test_encrypt():
    """Test encrypting a paste."""
    p = create_paste("test_encrypt")
    key = p.encrypt()
    assert key is not None
    with pytest.raises(ValueError):
        p.encrypt()


def test_decrypt():
    """Test decrypting a paste."""
    plaintext = "test_decrypt"
    p = AsyncPaste(content=plaintext)
    assert p.decrypt()
    key = p.encrypt()
    assert p.decrypt()
    assert p._content != p.content
    assert p.content == plaintext

    p2 = AsyncPaste(content=p._content, metadata=p.metadata)
    p2.decrypt(key)
    assert p2.content == plaintext
    p._key = None
    with pytest.raises(ValueError):
        p.decrypt()
