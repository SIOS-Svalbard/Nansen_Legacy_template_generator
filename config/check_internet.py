import http.client as httplib

def have_internet() -> bool:
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=1) # Check for maximum of 1 second
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()
