import { queryOptions } from '@tanstack/react-query';
import { fetchWeatherObservations, type WeatherFilters } from '../api/weather';

export const weatherQueryOptions = (filters: WeatherFilters = {}) =>
  queryOptions({
    queryKey: ['weather', filters],
    queryFn: () => fetchWeatherObservations(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
