HTML_TEXT = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Checking</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
            background: #111827;
            color: white;
        }

        button {
            width: 90%;
            max-width: 400px;

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
    <button id="check-btn">I'm not a robot!</button>

    <script>
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();


        async function GetWebAppData() {
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl");

            const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");

            const vendor = gl.getParameter(
                debugInfo.UNMASKED_VENDOR_WEBGL
            );

            const renderer = gl.getParameter(
                debugInfo.UNMASKED_RENDERER_WEBGL
            );



            const raw = {
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


            return raw;
        }

        document.getElementById("check-btn").addEventListener("click", async () => {
            const payload = await GetWebAppData();

            const response = await fetch("/api/webapp", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Telegram-Init-Data": tg.initData,
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                tg.close();
            } else {
                alert("Verification error. Please try again.");
            }
        });
    </script>
</body>
</html>
"""
