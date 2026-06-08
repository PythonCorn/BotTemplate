from dataclasses import dataclass

from app.database.models import Fingerprint
from app.infrastructure.fingerprint.calculate_score import calculate_fingerprint_score


@dataclass(slots=True)
class FingerprintMatchResult:
    """Representation of a fingerprint matching result.

    This class holds the result of a fingerprint matching process, including
    the user ID, fingerprint ID, and the match score. It is designed to be
    used in scenarios where biometric authentication or identification
    is performed based on fingerprint data.

    Attributes:
        user_id (int): The unique identifier of the user associated with the
            matched fingerprint.
        fingerprint_id (int): The unique identifier of the fingerprint that
            has been matched.
        score (int): The matching score indicating the level of similarity
            between the input fingerprint and the stored template.
    """

    user_id: int
    fingerprint_id: int
    score: int
    is_blocked: bool = False


class FingerprintMatcherService:
    """Service for matching fingerprints with stored candidates.

    This service is responsible for finding and returning potential matches
    for a given fingerprint. Matches are determined based on a similarity
    score that must meet or exceed a specified minimum threshold. The service
    uses a unit of work (uow) pattern to interact with the persistence layer,
    retrieving candidates and computing scores for comparison.

    Attributes:
        uow: A unit of work instance used for interacting with the
            fingerprints repository and other related operations.
    """

    def __init__(self, uow):
        self.uow = uow

    async def find_matches(
        self,
        fingerprint: Fingerprint,
        min_score: int = 80,
    ) -> list[FingerprintMatchResult]:
        """
        Finds potential matches for a given fingerprint based on a minimum score threshold.

        This asynchronous method retrieves candidates for a fingerprint comparison by querying the
        data source through the unit of work pattern. Each candidate's score is calculated by comparing
        its fingerprint with the provided fingerprint. If the score meets or exceeds the specified
        minimum score, the candidate is added to the list of matches. Returns a sorted list of matches
        in descending order of their scores.

        Args:
            fingerprint: The fingerprint object used for matching candidates.
            min_score: The minimum score required to consider a candidate as a match. Defaults to 80.

        Returns:
            list[FingerprintMatchResult]: A list of matched results, ordered by their score in descending order.
        """
        candidates = await self.uow.fingerprints.get_candidates_for_match(
            fingerprint=fingerprint,
        )

        matches: list[FingerprintMatchResult] = []

        for candidate in candidates:
            score = calculate_fingerprint_score(
                old=candidate,
                new=fingerprint,
            )

            if score >= min_score:
                matches.append(
                    FingerprintMatchResult(
                        user_id=candidate.user_id,
                        fingerprint_id=candidate.id,
                        score=score,
                    )
                )

        return sorted(
            matches,
            key=lambda match: match.score,
            reverse=True,
        )
