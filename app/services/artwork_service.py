import requests


_artwork_cache = {}


def download_artwork(url):
    if not url:
        return None

    if url in _artwork_cache:
        return _artwork_cache[url]

    try:
        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        image_data = response.content
        _artwork_cache[url] = image_data

        return image_data

    except requests.RequestException as error:
        print(f"Artwork download error: {error}")
        return None
