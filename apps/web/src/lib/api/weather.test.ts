import { describe, expect, it } from "bun:test";
import { buildWeatherQueryUrl } from "./weather";

describe("Weather API Client", () => {
  it("should construct default URL without filters", () => {
    const url = buildWeatherQueryUrl({}, "http://localhost:8000");
    expect(url).toBe("http://localhost:8000/api/v1/weather/");
  });

  it("should append query parameters correctly", () => {
    const url = buildWeatherQueryUrl(
      { location: "Forus", days: 14, limit: 50 },
      "http://localhost:8000"
    );
    expect(url).toContain("location=Forus");
    expect(url).toContain("days=14");
    expect(url).toContain("limit=50");
  });
});
