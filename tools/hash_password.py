from __future__ import annotations

import getpass
import hashlib
import secrets

password = getpass.getpass("Admin password: ")
salt = secrets.token_urlsafe(18)
iterations = 310_000
digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()
print(f"ADMIN_PASSWORD_HASH=pbkdf2_sha256${iterations}${salt}${digest}")
