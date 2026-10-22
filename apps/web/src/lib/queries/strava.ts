import { queryOptions } from '@tanstack/react-query';
import { fetchStravaStatus } from '../api/strava';

export const stravaStatusQueryOptions = () =>
  queryOptions({
    queryKey: ['strava', 'status'],
    queryFn: () => fetchStravaStatus(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
