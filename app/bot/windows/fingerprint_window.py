from aiogram.types import WebAppInfo

from app.bot.windows.core.base_window import BaseWindow
from app.bot.windows.core.window_message import WindowMessage
from app.services.fingerprint_match import FingerprintMatchResult


class FingerprintWindow(BaseWindow):
    def fingerprint_message(self, public_url: str, web_app_path: str) -> WindowMessage:
        keyboard = self.inline_keyboard()
        keyboard.button(
            text=self._("Условия"),
            web_app=WebAppInfo(url=f"{public_url}{web_app_path}"),
        )
        return self.message(
            caption=self._(
                "Для пользования ботом вам необходимо принять условия. Для этого нажмите на кнопку ниже!"
            ),
            reply_markup=keyboard.adjust(1).as_markup(),
            photo_filename="example.png",
        )

    def get_scams(self, user_id: int, match_result: list[FingerprintMatchResult]) -> WindowMessage:
        """
        Identifies and reports potential scam activities based on fingerprint match results.

        This method generates a message when a suspicious fingerprint is detected for a
        specific user. The message includes the user ID of the flagged individual and
        a list of other user IDs whose fingerprints match.

        Args:
            user_id (int): The ID of the user whose fingerprint is flagged as suspicious.
            match_result (list[FingerprintMatchResult]): A list of fingerprint match results
                containing information about users with matching fingerprints.

        Returns:
            str: A formatted message describing the suspicious fingerprint and the list
            of user IDs with matching fingerprints.
        """
        users = "\n".join(
            [
                f"• user_id: <code>{match.user_id}</code> — score: <b>{match.score} %</b>"
                for match in match_result
            ]
        )

        return self.message(
            text=(
                f"⚠️ Замечен подозрительный отпечаток пользователя:\n"
                f"<code>{user_id}</code>\n\n"
                f"Похожие пользователи:\n"
                f"{users}"
            )
        )
