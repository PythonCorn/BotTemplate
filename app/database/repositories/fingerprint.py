import logging

from sqlalchemy import and_, or_, select

from app.database.models import Fingerprint
from app.database.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class FingerprintRepository(BaseRepository[Fingerprint]):
    """Handles data operations for the Fingerprint entity.

    Provides methods for retrieving fingerprint records based on specific
    criteria and for retrieving potential matching candidates from the
    database.

    Attributes:
        session (AsyncSession): Database session interface used for
            executing queries and managing transactions.
    """

    async def get_by_hash_and_user_id(
        self, fingerprint_hash: str, user_id: int
    ) -> Fingerprint | None:
        """
        Fetches a fingerprint record that matches the given hash and user ID.

        This asynchronous method queries the database using the provided fingerprint
        hash and user ID and returns the corresponding fingerprint record, if it
        exists. If no matching fingerprint is found, the method returns None.

        Args:
            fingerprint_hash (str): The hash identifying the fingerprint to retrieve.
            user_id (int): The ID of the user associated with the fingerprint.

        Returns:
            Fingerprint | None: The fingerprint record matching the given criteria, or
            None if no match is found.
        """
        stmt = select(Fingerprint).where(
            Fingerprint.fingerprint_hash == fingerprint_hash, Fingerprint.user_id == user_id
        )
        result = await self.session.scalar(stmt)
        if result is not None:
            logger.info("Exists fingerprint %s", result)
        return result

    async def get_candidates_for_match(
        self,
        fingerprint: Fingerprint,
        limit: int = 100,
    ) -> list[Fingerprint]:
        """
        Retrieves a list of fingerprint candidates that match specific conditions for comparison.

        The function queries the database to find fingerprints that do not belong to the same user as the
        given fingerprint and meet certain matching criteria. These criteria include having the same
        fingerprint hash, the same renderer, or a combination of platform, screen width, and screen height.
        The result is then limited by the specified maximum number of candidates.

        Args:
            fingerprint (Fingerprint): The fingerprint to match against.
            limit (int): The maximum number of fingerprint candidates to retrieve. Defaults to 100.

        Returns:
            list[Fingerprint]: A list of fingerprints matching the specified conditions.
        """
        stmt = (
            select(Fingerprint)
            .where(Fingerprint.user_id != fingerprint.user_id)
            .where(
                or_(
                    Fingerprint.fingerprint_hash == fingerprint.fingerprint_hash,
                    Fingerprint.renderer == fingerprint.renderer,
                    and_(
                        Fingerprint.platform == fingerprint.platform,
                        Fingerprint.screen_width == fingerprint.screen_width,
                        Fingerprint.screen_height == fingerprint.screen_height,
                    ),
                )
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
