import os
import pytest
from unittest.mock import patch, MagicMock
from project import get_top, PDF, remove_token_cache

# Mock environment variables for testing
os.environ['CLIENT_ID'] = 'test_client_id'
os.environ['CLIENT_SECRET'] = 'test_client_secret'


def test_get_top():
    user_token = "test_user"
    duration = "long_term"

    # Mock the token retrieval and the Spotify API calls
    with patch('spotipy.util.prompt_for_user_token', return_value="test_token"):
        with patch('spotipy.Spotify') as mock_spotify:
            mock_spotify.return_value.current_user_top_tracks.return_value = {
                'items': [
                    {
                        'name': 'Track 1',
                        'artists': [{'name': 'Artist 1'}],
                        'album': {'images': [{'url': 'http://example.com/image1.jpg'}]}
                    },
                    {
                        'name': 'Track 2',
                        'artists': [{'name': 'Artist 2'}],
                        'album': {'images': [{'url': 'http://example.com/image2.jpg'}]}
                    }
                ]
            }

            # Call the function and check results
            tracks, image_urls = get_top(user_token, duration)

            # Assertions to verify the tracks and image URLs
            assert tracks == [('Track 1', 'Artist 1'), ('Track 2', 'Artist 2')]
            assert image_urls == ['http://example.com/image1.jpg', 'http://example.com/image2.jpg']


def test_pdf_initialization():
    title_duration = "Last 6 Months"
    pdf = PDF(title_duration)
    assert pdf is not None
    assert pdf.page_no() == 1  # Check that a new page is added


def test_remove_token_cache():
    user_token = "test_user"
    cache_file = f".cache-{user_token}"

    # Create a dummy cache file for testing
    with open(cache_file, 'w') as f:
        f.write("dummy token")

    remove_token_cache(user_token)

    # Check if the cache file is removed
    assert not os.path.exists(cache_file)
