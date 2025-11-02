import { useEffect } from 'react';
import { useAuth } from './AuthProvider';
import { addNotification } from './NotificationToast';

export function BackgroundMonitor() {
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    let lastReflectionCount = 0;
    let lastTaskCount = 0;

    const checkBackgroundActivity = async () => {
      try {
        const [reflectionsRes, tasksRes] = await Promise.all([
          fetch('http://localhost:8000/api/reflections/', {
            headers: { Authorization: `Bearer ${token}` }
          }).catch(() => ({ json: async () => [] })),
          fetch('http://localhost:8000/api/tasks/', {
            headers: { Authorization: `Bearer ${token}` }
          }).catch(() => ({ json: async () => [] }))
        ]);

        const reflections = await reflectionsRes.json();
        const tasks = await tasksRes.json();

        if (Array.isArray(reflections) && reflections.length > lastReflectionCount) {
          const newCount = reflections.length - lastReflectionCount;
          addNotification(
            `🔍 Reflection Loop: Generated ${newCount} new insight${newCount > 1 ? 's' : ''}`,
            'info'
          );
          lastReflectionCount = reflections.length;
        }

        if (Array.isArray(tasks)) {
          const autoTasks = tasks.filter((t: any) => t.auto_generated);
          if (autoTasks.length > lastTaskCount) {
            const newCount = autoTasks.length - lastTaskCount;
            addNotification(
              `🤖 Learning Engine: Created ${newCount} autonomous task${newCount > 1 ? 's' : ''}`,
              'success'
            );
            lastTaskCount = autoTasks.length;
          }
        }
      } catch (error) {
        console.error('Background monitor error:', error);
      }
    };

    const interval = setInterval(checkBackgroundActivity, 8000);
    checkBackgroundActivity();

    return () => clearInterval(interval);
  }, [token]);

  return null;
}
