from datetime import datetime

import pytest

from pastypy import Paste

TEST_SITE = "https://paste.zevs.me"


def get_content(test_name):
    return f"---\nTest: {test_name}\nTime: {datetime.utcnow().timestamp()}"


def create_paste(test_name):
    return Paste(content=get_content(test_name), site=TEST_SITE)


def test_create():
    """Test creating a paste."""
    p = create_paste("test_create")
    assert p.id is None


def test_repr():
    """Test paste.__repr__."""
    p = Paste(content="test_repr")
    assert p.__repr__() == "<Paste: content=test_repr, encrypted=False>"


def test_content():
    """Test content."""
    content = "test_content"
    p = Paste(content=content)
    assert content == p.content

    _ = p.encrypt()
    p._plaintext = None
    assert p.content == f"<Encrypted: {p._content}>"


def test_save_delete():
    """Test saving and deleting a paste."""
    p = create_paste("test_save")
    with pytest.raises(ValueError):
        p.delete()

    token = p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token
    assert p.url == f"{TEST_SITE}/{p.id}"

    p._token = None
    with pytest.raises(ValueError):
        p.delete()
    p.delete(token)


def test_edit():
    """Test editing a paste."""
    p = create_paste("test_edit")
    with pytest.raises(ValueError):
        p.edit(content="NI")

    content = p.content
    token = p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token

    p.edit(get_content("test_edit_post"))
    assert p.content != content
    p._token = None
    with pytest.raises(ValueError):
        p.edit(content="NI")
    p.delete(token)


def test_edit_enc():
    """Test editing an encrypted paste."""
    p = create_paste("test_edit_enc")
    key = p.encrypt()
    md = p.metadata
    p.save()

    new_key = p.edit(content="test_edit_enc_post")
    new_md = p.metadata
    assert key != new_key
    assert md != new_md
    p.delete()


def test_get():
    """Test getting a paste."""
    p = create_paste("test_get")
    token = p.save(site=TEST_SITE)
    assert p.id is not None
    assert p._token == token

    p2 = Paste.get(p.id, site=TEST_SITE)
    assert p.id == p2.id
    assert p.content == p2.content
    p.delete()


def test_encrypt():
    """Test encrypting a paste."""
    p = create_paste("test_encrypt")
    key = p.encrypt()
    assert key is not None
    with pytest.raises(ValueError):
        _ = p.encrypt()


def test_decrypt():
    """Test decrypting a paste."""
    plaintext = "test_decrypt"
    p = Paste(content=plaintext)
    assert p.decrypt()
    key = p.encrypt()
    assert p.decrypt()
    assert p._content != plaintext
    assert p.content == plaintext

    p2 = Paste(content=p._content, metadata=p.metadata)
    p2.decrypt(key)
    assert p2.content == plaintext
    p._key = None
    with pytest.raises(ValueError):
        p.decrypt()
