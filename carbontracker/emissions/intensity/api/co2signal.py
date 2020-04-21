import requests

from emissions.intensity.api.intensity_api import IntensityAPI
from emissions.intensity import intensity

AUTH_TOKEN = "2e7f70fa1f2ef4e5"
API_URL = "https://api.co2signal.com/v1/latest"

class CO2Signal(IntensityAPI):
    def suitable(self, g_location):
        return True

    def carbon_intensity(self, g_location, time_len=None):
        carbon_intensity = intensity.CarbonIntensity(g_location=g_location)

        try:
            ci = self._carbon_intensity_by_location(
                lon=g_location.lng, 
                lat=g_location.lat
            )
            carbon_intensity.carbon_intensity = ci
        except:
            ci = self._carbon_intensity_by_location(
                country_code=g_location.country
            )
            carbon_intensity.carbon_intensity = ci
            carbon_intensity.message = f"Failed to retrieve carbon intensity by coordinates. Fetched by country code {g_location.country} instead."

        return carbon_intensity

    def _carbon_intensity_by_location(self, lon=None, lat=None, country_code=None):
        """Retrieves carbon intensity (gCO2eq/kWh) by location.
        
        Note:
            Only use arguments (lon, lat) or country_code.
        
        Args:
            lon (float): Longitude. Defaults to None.
            lat (float): Lattitude. Defaults to None.
            country_code (str): Alpha-2 country code. Defaults to None.

        Returns:
            Carbon intensity in gCO2eq/kWh.
        
        Raises:
            UnitError: The unit of the carbon intensity does not match the
                expected unit.
        """
        if country_code is not None:
            params = (
                ("countryCode", country_code),
            )
            assert(lon is None and lat is None)
        elif lon is not None and lat is not None:
            params = (
                ("lon", lon),
                ("lat", lat)
            )
            assert(country_code is None)
        
        headers = {
            "auth-token": AUTH_TOKEN
        }

        response = requests.get(API_URL,
                                headers=headers,
                                params=params).json()
        carbon_intensity = response["data"]["carbonIntensity"]
        unit = response["units"]["carbonIntensity"]
        expected_unit = "gCO2eq/kWh"
        if unit != expected_unit:
            raise intensity.UnitError(expected_unit, unit,
                            "Carbon intensity query returned the wrong unit.")

        return carbon_intensity