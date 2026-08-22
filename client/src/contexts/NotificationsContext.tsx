import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export type NotificationItem = {
  id: string;
  type: string;
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
};

type ApiNotification = {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
};

function toNotificationItem(record: ApiNotification): NotificationItem {
  return {
    id: record.id,
    type: record.type,
    title: record.title,
    message: record.message,
    isRead: record.is_read,
    createdAt: record.created_at,
  };
}

type NotificationsContextValue = {
  notifications: NotificationItem[];
  unreadCount: number;
  markRead: (id: string) => void;
  markAllRead: () => void;
};

const NotificationsContext = createContext<NotificationsContextValue | null>(null);

export function NotificationsProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const load = useCallback(async () => {
    const response = await apiFetch("/api/notifications");
    if (!response.ok) return;
    const data: ApiNotification[] = await response.json();
    setNotifications(data.map(toNotificationItem));
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void load();
    } else if (status === "unauthenticated") {
      setNotifications([]);
    }
  }, [status, load]);

  const markRead = useCallback((id: string) => {
    const previous = notifications;
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, isRead: true } : n));
    apiFetch(`/api/notifications/${id}/read`, { method: "PATCH" })
      .then((response) => {
        if (!response.ok) throw new Error("Unable to update notification");
      })
      .catch(() => setNotifications(previous));
  }, [notifications]);

  const markAllRead = useCallback(() => {
    const previous = notifications;
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
    apiFetch("/api/notifications/mark-all-read", { method: "POST" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to update notifications");
        const data: ApiNotification[] = await response.json();
        setNotifications(data.map(toNotificationItem));
      })
      .catch(() => setNotifications(previous));
  }, [notifications]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return <NotificationsContext.Provider value={{ notifications, unreadCount, markRead, markAllRead }}>{children}</NotificationsContext.Provider>;
}

export function useNotifications() {
  const value = useContext(NotificationsContext);
  if (!value) throw new Error("useNotifications must be used inside NotificationsProvider");
  return value;
}
