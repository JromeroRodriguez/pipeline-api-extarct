import unittest
from pathlib import Path
from unittest.mock import patch

from src.transform import transform


class TransformValidationTests(unittest.TestCase):
	def setUp(self):
		self.raw_data = [
			{
				"city": "Bogota",
				"latitude": 4.711,
				"longitude": -74.0721,
				"data": {
					"hourly": {
						"time": ["2026-10-08T00:00"],
						"temperature_2m": [15.0],
						"relative_humidity_2m": [80],
						"precipitation": [0.0],
						"wind_speed_10m": [3.0],
					}
				},
			}
		]

	@patch("src.transform.get_latest_raw_file", return_value=Path("weather.json"))
	@patch("src.transform.load_raw_data")
	def test_transform_returns_validated_dataframe(self, load_raw_data, _get_latest_raw_file):
		load_raw_data.return_value = self.raw_data

		dataframe = transform()

		self.assertEqual(len(dataframe), 1)
		self.assertEqual(dataframe.loc[0, "city"], "Bogota")

	@patch("src.transform.get_latest_raw_file", return_value=Path("weather.json"))
	@patch("src.transform.load_raw_data")
	def test_transform_rejects_invalid_dataframe(self, load_raw_data, _get_latest_raw_file):
		invalid_data = [
			{
				**self.raw_data[0],
				"data": {
					"hourly": {
						**self.raw_data[0]["data"]["hourly"],
						"relative_humidity_2m": [None],
					}
				},
			}
		]
		load_raw_data.return_value = invalid_data

		with self.assertRaises(ValueError):
			transform()


if __name__ == "__main__":
	unittest.main()
