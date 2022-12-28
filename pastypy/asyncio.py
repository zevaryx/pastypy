"""AsyncIO Paste wrapper."""
from typing import Optional

from aiohttp import ClientSession

from pastypy.sync import Paste


class AsyncPaste(Paste):
    @classmethod
    async def get(cls, id: str, site: Optional[str] = "https://pasty.lus.pm") -> "AsyncPaste":
        """
        Get a paste.

        Args:
            id: ID of paste to get

        Returns:
            New Paste instance
        """
        endpoint = site + "/api/v2/pastes/"
        async with ClientSession() as session:
            resp = await session.get(endpoint + id)
            resp.raise_for_status()
            raw = await resp.json(content_type="text/plain")
        raw["site"] = site
        return cls(**raw)

    @classmethod
    async def report(cls, target: "Paste | str", reason: str, site: Optional[str] = "https://pasty.lus.pm") -> str:
        """
        Report a paste.

        Args:
            target: Paste or paste ID
            site: Target site, default official
        """
        if isinstance(target, cls):
            target = target.id

        endpoint = site + f"/api/v2/pastes/{target}/report"
        async with ClientSession() as session:
            resp = await session.get(endpoint)
            if resp.status == 404:
                return "This site does not support reporting"
            resp.raise_for_status()

            raw = await resp.json(content_type="text/plain")

        if not raw["success"]:
            return f"Failed to report message: {raw['message']}"

        return f"Reported message: {raw['message']}"

    async def save(self, site: Optional[str] = "https://pasty.lus.pm") -> str:
        """
        Save a paste to the designated pasty instance

        Args:
            site: Pasty instance, default official

        Returns:
            Modification token
        """
        if not self._site:
            self._site = site
        endpoint = self._site + "/api/v2/pastes"

        payload = {
            "content": self._content,
            "metadata": self.metadata,
        }

        async with ClientSession() as session:
            resp = await session.post(endpoint, json=payload)
            resp.raise_for_status()
            raw = await resp.json(content_type="text/plain")

        self.id = raw["id"]
        self.metadata = raw["metadata"]
        self.created = raw["created"]
        self._token = raw["modificationToken"]

        return self._token

    async def edit(
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
        new_p = AsyncPaste(
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

        async with ClientSession(headers=headers) as session:
            resp = await session.patch(endpoint + self.id, json=payload, headers=headers)
            resp.raise_for_status()

        self._content = new_p._content
        self._plaintext = new_p._plaintext
        self._key = new_p._key
        self.metadata = new_p.metadata

        return key  # noqa: R504

    async def delete(
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

        async with ClientSession(headers=headers) as session:
            resp = await session.delete(endpoint + self.id, headers=headers)
            resp.raise_for_status()
