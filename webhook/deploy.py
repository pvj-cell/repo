#!/usr/bin/env python3
import hmac
import hashlib
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# Твій секрет та шлях
SECRET = b"3181d1fadeb2206ce4bec1a10fc3599fa1b22255a29c93250fdf3d61cdacd537"
DEPLOY_DIR = "/var/www/test.xpro.com.ua"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # Перевірка підпису GitHub
        sig = self.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected):
            self.send_response(403)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

        # Покращений ланцюжок команд з логуванням у файл deploy_debug.log
        # Ми примусово скидаємо власника перед git reset, щоб не було Permission Denied
        deploy_command = (
            f"cd {DEPLOY_DIR} && "
            "{ "
            "echo '--- Starting deploy at $(date) ---'; "
            "sudo /usr/bin/chown -R deploy:deploy . ; "
            "/usr/bin/git fetch origin main ; "
            "/usr/bin/git reset --hard origin/main ; "
            "sudo /usr/bin/cp -rf catalog admin system ./html/ ; "
            "sudo /usr/bin/chown -R www-data:www-data ./html/system/storage ./html/image ; "
            "sudo /usr/bin/chmod -R 775 ./html/system/storage ./html/image ; "
            "/usr/bin/docker exec opencart-site rm -rf /var/www/html/system/storage/cache/template/* ; "
            "echo '--- Deploy finished ---'; "
            "} >> /var/www/test.xpro.com.ua/deploy_debug.log 2>&1"
        )

        subprocess.Popen(["/bin/bash", "-c", deploy_command])

    def log_message(self, format, *args):
        # Ігноруємо логування в консоль, щоб не забивати nohup.out
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9000), WebhookHandler)
    print("Webhook listener on port 9000 is active...")
    server.serve_forever()
