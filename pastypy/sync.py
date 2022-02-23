"""Paste wrapper."""
from binascii import hexlify
from typing import Optional

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class Paste:
    def __init__(
        self,
        content: str,
        id: Optional[str] = None,
        created: Optional[int] = None,
        metadata: Optional[dict] = None,
        site: Optional[str] = None,
    ):
        self._content = content
        self.id = id
        self.created = created
        self.metadata = metadata or {}
        self._site = site

        self.encrypted = "pf_encryption" in self.metadata
        self._plaintext = None if self.encrypted else self._content
        self._token = None
        self._key = None

    def __repr__(self):
        return f"<Paste: content={self.content}, encrypted={self.encrypted}>"

    @classmethod
    def get(cls, id: str, site: Optional[str] = "https://pasty.lus.pm") -> "Paste":
        """
        Get a paste.

        Args:
            id: ID of paste to get

        Returns:
            New Paste instance
        """
        endpoint = site + "/api/v2/pastes/"
        resp = requests.get(endpoint + id)
        resp.raise_for_status()
        raw = resp.json()
        raw["site"] = site
        return cls(**raw)

    @property
    def content(self) -> str:
        """Get the Paste contents."""
        return self._plaintext or f"<Encrypted: {self._content}>"

    @property
    def url(self) -> str:
        """Get the Paste URL."""
        if self.id:
            return self._site + f"/{self.id}"

    def encrypt(self) -> str:
        """
        Encrypt a paste.

        Returns:
            Hexlified key

        Raises:
            ValueError: Cannot encrypt encrypted paste
        """
        if self.encrypted:
            raise ValueError("Cannot encrypt encrypted paste")
        key = get_random_bytes(32)
        cipher = AES.new(key, mode=AES.MODE_CBC)
        iv = cipher.iv
        ct = cipher.encrypt(pad(self._content.encode("UTF-8"), AES.block_size))
        self._plaintext = self._content
        self._content = hexlify(ct).decode("UTF8")
        self._key = key
        self.metadata["pf_encryption"] = {"alg": "AES-CBC", "iv": hexlify(iv).decode("UTF8")}
        self.encrypted = True
        return hexlify(key).decode("UTF8")

    def decrypt(self, key: Optional[str] = None) -> bool:
        """
        Decrypt a paste

        Args:
            key: Decryption key

        Returns:
            If decryption was successful
        """
        if not self.encrypted:
            return True
        if not any([self._key, key]):
            raise ValueError("Key required if not encrypted/decrypted locally")
        key = self._key or bytes.fromhex(key)
        iv = bytes.fromhex(self.metadata["pf_encryption"]["iv"])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = cipher.decrypt(bytes.fromhex(self._content))
        self._plaintext = unpad(padded, AES.block_size).decode("UTF8")
        self._key = key
        return True

    def save(self, site: Optional[str] = "https://pasty.lus.pm") -> str:
        """
        Save a paste to the designated pasty instance

        Args:
            site: Pasty instance, default official

        Returns:
            Modification token
        """
        site = self._site or site
        self._site = site
        endpoint = site + "/api/v2/pastes"

        payload = {
            "content": self._content,
            "metadata": self.metadata,
        }

        resp = requests.post(endpoint, json=payload)
        resp.raise_for_status()
        raw = resp.json()

        self.id = raw["id"]
        self.metadata = raw["metadata"]
        self.created = raw["created"]
        self._token = raw["modificationToken"]

        return self._token

    def edit(
        self,
        content: str,
        modification_token: Optional[str] = None,
        site: Optional[str] = "https://pasty.lus.pm",
    ) -> Optional[str]:
        """
        Edit an existing paste.

        Args:
            content: New content
            modification_token: Modification token
            site: Pasty instance, default official

        Returns:
            New key if necessary

        Raises:
            ValueError: Unsaved Paste or missing token
        """
        site = self._site or site
        endpoint = site + "/api/v2/pastes/"

        if not self.id:
            raise ValueError("Paste must be saved before editing")

        token = self._token or modification_token
        if not token:
            raise ValueError("Token required to edit Paste")

        self._token = token
        key = None
        if self.encrypted:
            _ = self.metadata.pop("pf_encryption")
        new_p = Paste(
            content=content,
            id=self.id,
            created=self.created,
            metadata=self.metadata,
            site=self._site,
        )
        if self.encrypted:
            key = new_p.encrypt()

        payload = {"content": new_p._content, "metadata": new_p.metadata}

        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.patch(endpoint + self.id, json=payload, headers=headers)
        resp.raise_for_status()
        self._content = new_p._content
        self._plaintext = new_p._plaintext
        self._key = new_p._key
        self.metadata = new_p.metadata

        return key  # noqa: R504

    def delete(
        self, modification_token: Optional[str] = None, site: Optional[str] = "https://pasty.lus.pm"
    ) -> None:
        """
        Delete a paste.

        Args:
            modification_token: Modification token
            site: Pasty instance, default official

        Raises:
            ValueError: Unsaved Paste or missing token
        """
        site = self._site or site
        endpoint = site + "/api/v2/pastes/"

        if not self.id:
            raise ValueError("Paste must be saved before deleting")

        token = self._token or modification_token
        if not token:
            raise ValueError("Token required to delete Paste")

        self._token = token

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.delete(endpoint + self.id, headers=headers)
        resp.raise_for_status()
