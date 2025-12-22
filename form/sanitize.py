import base64


def sanitize_for_form(s: str) -> str:
    """
    Sanitizes a string so it contains ONLY:
    a-z A-Z 0-9 _ -

    Achieved using URL-safe Base64 encoding (RFC 4648) with padding removed.
    Fully reversible via `unsanitize_for_form`.

    ✅ Output chars: [A-Za-z0-9_-]
    ✅ Safe for form names, IDs, URL segments
    ✅ Unicode-safe (UTF-8)
    """
    # UTF-8 encode → bytes
    data = s.encode("utf-8")

    # URL-safe base64 encode → bytes
    b64 = base64.urlsafe_b64encode(data)

    # Convert to str and strip padding
    return b64.decode("ascii").rstrip("=")


def unsanitize_for_form(safe: str) -> str:
    """
    Restores the original string from a sanitized value
    created by `sanitize_for_form`.

    Fully reversible.
    """
    try:
        # Restore padding to multiple of 4
        pad_len = (4 - (len(safe) % 4)) % 4
        padded = safe + ("=" * pad_len)

        # URL-safe base64 decode → bytes
        data = base64.urlsafe_b64decode(padded)

        # UTF-8 decode → str
        return data.decode("utf-8")
    except Exception as e:
        print(f"⚠️ failed to unsanitize string {safe}: {e}")
        print("falling back to passed string")
        return safe
