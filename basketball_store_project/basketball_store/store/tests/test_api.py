from unittest.mock import patch
from store.views import get_weather, get_random_basketball_player

@patch('store.views.requests.get')
def test_get_weather_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'current_weather': {'temperature': 15.5, 'windspeed': 10}
    }
    weather = get_weather()
    assert weather['temperature'] == 15.5

@patch('store.views.requests.get')
def test_get_weather_failure(mock_get):
    mock_get.side_effect = Exception('API error')
    weather = get_weather()
    assert weather is None

@patch('store.views.requests.get')
def test_basketball_api_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'data': [
            {'first_name': 'LeBron', 'last_name': 'James', 'team': {'full_name': 'Lakers'}, 'position': 'F'},
            {'first_name': 'Stephen', 'last_name': 'Curry', 'team': {'full_name': 'Warriors'}, 'position': 'G'},
        ]
    }
    player = get_random_basketball_player()
    assert player is not None
    assert 'first_name' in player