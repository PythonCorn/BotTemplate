HTML_TEXT = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Terms of Use</title>

    <script src="https://telegram.org/js/telegram-web-app.js"></script>

    <style>
        body {
            margin: 0;
            height: 100vh;
            background: #111827;
            color: white;
            font-family: Arial, sans-serif;
        }

        .container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 16px;
            box-sizing: border-box;
        }

        .terms {
            flex: 1;
            overflow-y: auto;
            background: #1f2937;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            line-height: 1.6;
        }

        h1 {
            margin-top: 0;
        }

        button {
            width: 100%;
            min-height: 64px;
            font-size: 22px;
            padding: 16px;
            border: none;
            border-radius: 14px;
            cursor: pointer;
        }
    </style>
</head>

<body>
    <div class="container">

        <div class="terms">
            <h1>Terms of Use</h1>

            <p>
                By using this bot, you agree to these terms and conditions.
            </p>

            <p>
                The bot is provided "as is" without any warranties.
                The administration is not responsible for possible losses,
                interruptions, or misuse of the service.
            </p>

            <p>
                You agree not to use the bot for illegal activities,
                fraud, spam, harassment, or any actions that violate
                applicable laws.
            </p>

            <p>
                We may collect technical information required for
                security purposes, including IP address, device
                information, browser information, and Telegram account
                identifiers.
            </p>

            <p>
                Access to the service may be suspended or terminated
                without prior notice if suspicious or malicious activity
                is detected.
            </p>

            <p>
                Continued use of the bot constitutes acceptance of
                these terms.
            </p>

            <p>
                Last updated: 2026-06-05
            </p>

            <p>
                --------------------------------------------------------
            </p>

            <p>
                By pressing the button below, you confirm that you have
                read and accepted these terms of use.
            </p>
        </div>

        <button id="check-btn">
            I accept the terms
        </button>

    </div>

    <script>
        const tg = window.Telegram.WebApp;

        tg.ready();
        tg.expand();

        async function GetWebAppData() {
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl");

            const debugInfo = gl?.getExtension(
                "WEBGL_debug_renderer_info"
            );

            const vendor = debugInfo
                ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL)
                : null;

            const renderer = debugInfo
                ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                : null;

            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                devicePixelRatio: window.devicePixelRatio,
                hardwareConcurrency: navigator.hardwareConcurrency,
                maxTouchPoints: navigator.maxTouchPoints,
                vendor: vendor,
                renderer: renderer,
                device_platform: tg.platform,
                version: tg.version
            };
        }

        document.getElementById("check-btn").addEventListener(
            "click",
            async () => {
                const payload = await GetWebAppData();

                const response = await fetch("/api/webapp", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Telegram-Init-Data": tg.initData
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    tg.close();
                } else {
                    alert(
                        "Verification error. Please try again."
                    );
                }
            }
        );
    </script>
</body>
</html>
"""
