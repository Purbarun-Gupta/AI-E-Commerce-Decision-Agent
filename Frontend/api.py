
import os
import requests

API_BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:5000"
).rstrip("/")


def api_get(endpoint, params=None):
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        return {
            "error": str(exc),
            "url": url
        }

    except ValueError as exc:
        return {
            "error": f"Invalid JSON response: {exc}",
            "url": url
        }


def api_post(endpoint, payload):
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=90
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as exc:
        return {
            "error": str(exc),
            "status_code": response.status_code,
            "details": response.text[:1000],
            "url": url
        }

    except requests.exceptions.RequestException as exc:
        return {
            "error": str(exc),
            "url": url
        }

    except ValueError as exc:
        return {
            "error": f"Invalid JSON response: {exc}",
            "url": url
        }


def api_put(endpoint, data=None):
    """Send a PUT request to the Flask backend."""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.put(
            url,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        error = str(exc)

        # Include the backend's error message when available.
        if getattr(exc, "response", None) is not None:
            try:
                details = exc.response.json()
                if isinstance(details, dict):
                    error = details.get("error", error)
            except ValueError:
                pass

        return {
            "error": error,
            "url": url,
        }

    except ValueError as exc:
        return {
            "error": f"Invalid JSON response: {exc}",
            "url": url,
        }
