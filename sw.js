self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : {};
    
    const title = data.title || 'WeYoung 2025 Vote Visualizer - lzhoang2801';
    const options = {
        body: data.body || 'Có biến động vote mới!',
        icon: data.icon || 'https://event.mediacdn.vn/web_images/we_young_2025/wy-logo.svg',
        badge: 'https://event.mediacdn.vn/web_images/we_young_2025/wy-logo.svg',
        data: { url: data.url || '/wca-votes/' }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({type: 'window'}).then(windowClients => {
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                if (client.url === event.notification.data.url && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});