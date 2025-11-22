// Screen Capture API TypeScript declarations

interface DisplayMediaStreamConstraints extends MediaStreamConstraints {
  video?: boolean | MediaTrackConstraints & {
    displaySurface?: 'monitor' | 'window' | 'browser';
  };
  audio?: boolean | MediaTrackConstraints;
}

declare global {
  interface Navigator {
    mediaDevices: MediaDevices;
  }

  interface MediaDevices {
    getDisplayMedia(constraints?: DisplayMediaStreamConstraints): Promise<MediaStream>;
  }
}

export {};