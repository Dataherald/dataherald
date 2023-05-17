import { AMPLITUDE_API_KEY } from '@/env-variables';
import * as amplitude from '@amplitude/analytics-browser';

class AnalyticsService {
  constructor() {
    if (typeof window !== 'undefined' && AMPLITUDE_API_KEY) {
      amplitude.init(AMPLITUDE_API_KEY, undefined, {
        defaultTracking: {
          sessions: true,
          pageViews: true,
          formInteractions: true,
          fileDownloads: true,
        },
      });
    }
  }

  track(eventName: string, eventData: Record<string, unknown>) {
    amplitude.track(eventName, eventData);
  }

  setUser(properties: Record<string, amplitude.Types.ValidPropertyType>): void {
    const identify = new amplitude.Identify();
    for (const key in properties) {
      identify.set(key, properties[key]);
    }
  }
}

const analyticsService = new AnalyticsService();

export default analyticsService;
