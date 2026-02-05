class NotificationManager {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.badge = document.getElementById('notification-badge');
        this.notificationList = document.getElementById('notification-list');
        this.init();
    }
    
    init() {
        this.loadNotifications();
        setInterval(() => this.loadNotifications(), this.updateInterval);
        
        // Mark as read when dropdown is shown
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.addEventListener('shown.bs.dropdown', () => {
                this.markVisibleAsRead();
            });
        }
    }
    
    async loadNotifications() {
        try {
            // Load unread count
            const countResponse = await fetch('/notifications/api/unread-count/');
            const countData = await countResponse.json();
            this.updateBadge(countData.unread_count);
            
            // Load recent notifications
            const notifResponse = await fetch('/notifications/api/recent/');
            const notifData = await notifResponse.json();
            this.updateNotificationList(notifData.notifications);
            
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }
    
    updateBadge(count) {
        if (this.badge) {
            if (count > 0) {
                this.badge.textContent = count > 99 ? '99+' : count;
                this.badge.style.display = 'block';
            } else {
                this.badge.style.display = 'none';
            }
        }
    }
    
    updateNotificationList(notifications) {
        if (!this.notificationList) return;
        
        if (notifications.length === 0) {
            this.notificationList.innerHTML = `
                <li class="text-center py-3">
                    <small class="text-muted">No new notifications</small>
                </li>
            `;
            return;
        }
        
        this.notificationList.innerHTML = notifications.map(notif => `
            <li class="dropdown-item-text px-3 py-2 border-bottom ${notif.is_recent ? 'bg-light' : ''}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1 small">${notif.title}</h6>
                        <p class="mb-1 small">${notif.message}</p>
                        <small class="text-muted">${notif.created_at}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-success ms-2 mark-read-btn" 
                            data-notification-id="${notif.id}" title="Mark as read">
                        ✓
                    </button>
                </div>
            </li>
        `).join('');
        
        // Add event listeners to mark-as-read buttons
        this.notificationList.querySelectorAll('.mark-read-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAsRead(btn.dataset.notificationId);
                btn.remove();
            });
        });
    }
    
    async markAsRead(notificationId) {
        try {
            await fetch(`/notifications/mark-read/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            this.loadNotifications(); // Refresh counts
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    markVisibleAsRead() {
        // Mark all visible notifications as read when dropdown is opened
        if (this.notificationList) {
            const notificationIds = [];
            this.notificationList.querySelectorAll('.mark-read-btn').forEach(btn => {
                notificationIds.push(btn.dataset.notificationId);
            });
            
            notificationIds.forEach(id => this.markAsRead(id));
        }
    }
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NotificationManager();
});
