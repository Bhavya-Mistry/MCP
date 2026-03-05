from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("weather-mcp")


@mcp.tool()
def get_weather(city: str) -> dict:
    """Get current weather for a city"""

    url = f"http://wttr.in/{city}?format=j1"

    response = requests.get(url)
    data = response.json()

    # temp = data["current_condition"][0]["temp_C"]
    # condition = data["current_condition"][0]["weatherDesc"][0]["value"]

    return {"city": city, "data": data}


if __name__ == "__main__":
    mcp.run()
