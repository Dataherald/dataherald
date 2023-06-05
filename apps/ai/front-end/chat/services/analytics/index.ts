import { AMPLITUDE_API_KEY } from '@/env-variables';
import * as amplitude from '@amplitude/analytics-browser';
import { UserProfile } from '@auth0/nextjs-auth0/client';

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
      amplitude.setTransport(amplitude.Types.TransportType.SendBeacon);
    }
  }

  buttonClick(
    type: string,
    extraProperties: Record<string, unknown> = {},
  ): void {
    this.track('button-click', { type, ...extraProperties });
  }

  track(eventName: string, eventData: Record<string, unknown> = {}) {
    amplitude.track(eventName, eventData);
  }

  setUser(user: UserProfile): void {
    const identifyEvent = new amplitude.Identify();
    for (const key in user) {
      identifyEvent.set(key, user[key] as amplitude.Types.ValidPropertyType);
    }
    amplitude.identify(identifyEvent);
  }
}

const analyticsService = new AnalyticsService();

export default analyticsService;
