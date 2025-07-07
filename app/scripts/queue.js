(function() {
    'use strict';
    
    // Configuration
    const config = {
        apiKey: null,
        callbackUrl: null,
        lang: 'en',
        theme: 'light',
        pollInterval: 5000,
        maxPollAttempts: 60, // 5 minutes
        apiBaseUrl: window.location.origin
    };
    
    // Localization
    const messages = {
        en: {
            joining: 'Joining queue...',
            waiting: 'You are in the queue. Please wait...',
            position: 'Position in queue: {position}',
            ready: 'You are ready! Redirecting...',
            error: 'An error occurred. Please try again.',
            expired: 'Your session has expired. Please join again.',
            cancelled: 'Queue session cancelled.'
        },
        ar: {
            joining: 'الانضمام إلى الطابور...',
            waiting: 'أنت في الطابور. يرجى الانتظار...',
            position: 'الموقع في الطابور: {position}',
            ready: 'أنت جاهز! إعادة التوجيه...',
            error: 'حدث خطأ. يرجى المحاولة مرة أخرى.',
            expired: 'انتهت صلاحية جلستك. يرجى الانضمام مرة أخرى.',
            cancelled: 'تم إلغاء جلسة الطابور.'
        }
    };
    
    // Queue Manager Class
    class QueueManager {
        constructor(options = {}) {
            this.options = { ...config, ...options };
            this.token = null;
            this.pollCount = 0;
            this.pollInterval = null;
            this.statusElement = null;
            this.init();
        }
        
        init() {
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            this.options.apiKey = this.options.apiKey || urlParams.get('app_api_key');
            this.options.callbackUrl = this.options.callbackUrl || urlParams.get('callback_url');
            this.options.lang = this.options.lang || urlParams.get('lang') || 'en';
            this.options.theme = this.options.theme || urlParams.get('theme') || 'light';
            
            // Create status element
            this.createStatusElement();
            
            // Apply theme
            this.applyTheme();
        }
        
        createStatusElement() {
            this.statusElement = document.createElement('div');
            this.statusElement.id = 'queue-status';
            this.statusElement.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${this.options.theme === 'dark' ? '#333' : '#fff'};
                color: ${this.options.theme === 'dark' ? '#fff' : '#333'};
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                font-family: Arial, sans-serif;
                font-size: 14px;
                max-width: 300px;
                border: 1px solid ${this.options.theme === 'dark' ? '#555' : '#ddd'};
            `;
            document.body.appendChild(this.statusElement);
        }
        
        applyTheme() {
            if (this.options.theme === 'dark') {
                document.body.style.backgroundColor = '#1a1a1a';
                document.body.style.color = '#fff';
            }
        }
        
        updateStatus(message, type = 'info') {
            if (!this.statusElement) return;
            
            const colors = {
                info: this.options.theme === 'dark' ? '#4CAF50' : '#2196F3',
                success: '#4CAF50',
                error: '#f44336',
                warning: '#ff9800'
            };
            
            this.statusElement.style.borderLeft = `4px solid ${colors[type]}`;
            this.statusElement.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 5px;">
                    ${this.getMessage('queueTitle') || 'Queue Status'}
                </div>
                <div>${message}</div>
            `;
        }
        
        getMessage(key, params = {}) {
            const msg = messages[this.options.lang]?.[key] || messages.en[key] || key;
            return msg.replace(/\{(\w+)\}/g, (match, param) => params[param] || match);
        }
        
        async joinQueue(queueId, visitorId) {
            try {
                this.updateStatus(this.getMessage('joining'));
                
                const response = await fetch(`${this.options.apiBaseUrl}/join`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'app_api_key': this.options.apiKey
                    },
                    body: JSON.stringify({
                        queue_id: queueId,
                        visitor_id: visitorId
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                this.token = data.token;
                
                if (data.status === 'ready') {
                    this.handleReady(data);
                } else {
                    this.startPolling();
                }
                
            } catch (error) {
                console.error('Error joining queue:', error);
                this.updateStatus(this.getMessage('error'), 'error');
            }
        }
        
        startPolling() {
            this.pollCount = 0;
            this.pollInterval = setInterval(() => {
                this.checkStatus();
            }, this.options.pollInterval);
        }
        
        async checkStatus() {
            if (!this.token) return;
            
            try {
                this.pollCount++;
                
                const response = await fetch(`${this.options.apiBaseUrl}/queue_status?token=${this.token}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                switch (data.status) {
                    case 'ready':
                        this.handleReady(data);
                        break;
                    case 'expired':
                        this.handleExpired();
                        break;
                    case 'rejected':
                        this.handleCancelled();
                        break;
                    case 'waiting':
                        this.handleWaiting();
                        break;
                }
                
            } catch (error) {
                console.error('Error checking status:', error);
                if (this.pollCount >= this.options.maxPollAttempts) {
                    this.updateStatus(this.getMessage('error'), 'error');
                    this.stopPolling();
                }
            }
        }
        
        handleReady(data) {
            this.updateStatus(this.getMessage('ready'), 'success');
            this.stopPolling();
            
            // Redirect after a short delay
            setTimeout(() => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else if (this.options.callbackUrl) {
                    window.location.href = this.options.callbackUrl;
                }
            }, 2000);
        }
        
        handleWaiting() {
            this.updateStatus(this.getMessage('waiting'));
        }
        
        handleExpired() {
            this.updateStatus(this.getMessage('expired'), 'error');
            this.stopPolling();
        }
        
        handleCancelled() {
            this.updateStatus(this.getMessage('cancelled'), 'warning');
            this.stopPolling();
        }
        
        stopPolling() {
            if (this.pollInterval) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
            }
        }
        
        cancel() {
            if (!this.token) return;
            
            fetch(`${this.options.apiBaseUrl}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: this.token })
            }).catch(console.error);
            
            this.handleCancelled();
        }
        
        destroy() {
            this.stopPolling();
            if (this.statusElement) {
                this.statusElement.remove();
                this.statusElement = null;
            }
        }
    }
    
    // Expose to global scope
    window.QueueManager = QueueManager;
    
    // Auto-initialize if parameters are present
    const urlParams = new URLSearchParams(window.location.search);
    const queueId = urlParams.get('queue_id');
    const visitorId = urlParams.get('visitor_id');
    
    if (queueId && visitorId) {
        const queueManager = new QueueManager();
        queueManager.joinQueue(queueId, visitorId);
    }
    
})(); 