/**
 * Transcendence IDE WebSocket Client
 * Handles real-time file operations, execution, and security scanning
 */

class IDEWebSocketClient {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.connected = false;
        this.messageHandlers = new Map();
        this.pendingRequests = new Map();
        this.requestId = 0;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    /**
     * Connect to WebSocket server
     */
    async connect() {
        return new Promise((resolve, reject) => {
            const wsUrl = `ws://localhost:8000/ide/ws?token=${this.token}`;
            
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('✓ IDE WebSocket connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                resolve();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.connected = false;
                this.attemptReconnect();
            };
        });
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.emit('connection_lost');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect().catch(err => {
                console.error('Reconnection failed:', err);
            });
        }, delay);
    }

    /**
     * Send message with promise-based response
     */
    async send(type, data = {}) {
        if (!this.connected) {
            throw new Error('WebSocket not connected');
        }

        const requestId = ++this.requestId;
        const message = { type, ...data, requestId };

        return new Promise((resolve, reject) => {
            this.pendingRequests.set(requestId, { resolve, reject });

            this.ws.send(JSON.stringify(message));

            setTimeout(() => {
                if (this.pendingRequests.has(requestId)) {
                    this.pendingRequests.delete(requestId);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
        });
    }

    /**
     * Handle incoming message
     */
    handleMessage(message) {
        const { type, requestId } = message;

        if (requestId && this.pendingRequests.has(requestId)) {
            const { resolve } = this.pendingRequests.get(requestId);
            this.pendingRequests.delete(requestId);
            resolve(message);
        }

        if (this.messageHandlers.has(type)) {
            this.messageHandlers.get(type)(message);
        }

        this.emit('message', message);
    }

    /**
     * Register message handler
     */
    on(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    /**
     * Emit event to listeners
     */
    emit(event, data) {
        const listeners = this.messageHandlers.get(event) || [];
        if (typeof listeners === 'function') {
            listeners(data);
        }
    }

    /**
     * File Operations
     */

    async fileOpen(path) {
        return this.send('file_open', { path });
    }

    async fileSave(path, content) {
        return this.send('file_save', { path, content });
    }

    async fileCreate(path, content = '') {
        return this.send('file_create', { path, content });
    }

    async fileDelete(path) {
        return this.send('file_delete', { path });
    }

    async fileRename(oldPath, newPath) {
        return this.send('file_rename', { old_path: oldPath, new_path: newPath });
    }

    async directoryList() {
        return this.send('directory_list');
    }

    /**
     * Code Execution
     */

    async executeCode(language, code, filePath = null) {
        return this.send('code_execute', { language, code, file_path: filePath });
    }

    /**
     * Security Operations
     */

    async securityScan(filePath) {
        return this.send('security_scan', { file_path: filePath });
    }

    async autoFix(filePath, issue) {
        return this.send('auto_fix', { file_path: filePath, issue });
    }

    async autoQuarantine(filePath) {
        return this.send('auto_quarantine', { file_path: filePath });
    }

    /**
     * Disconnect
     */
    disconnect() {
        if (this.ws) {
            this.connected = false;
            this.ws.close();
        }
    }
}

/**
 * IDE Manager - High-level API for IDE operations
 */
class IDEManager {
    constructor(client) {
        this.client = client;
        this.currentFile = null;
        this.fileTree = null;
    }

    async openFile(path) {
        const result = await this.client.fileOpen(path);
        
        if (result.type === 'file_opened') {
            this.currentFile = {
                path: result.path,
                content: result.content,
                size: result.size,
                modified: false
            };
            return this.currentFile;
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async saveFile(path, content) {
        const result = await this.client.fileSave(path, content);
        
        if (result.type === 'file_saved') {
            if (this.currentFile && this.currentFile.path === path) {
                this.currentFile.modified = false;
            }
            return result;
        } else if (result.type === 'file_save_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'file_save_pending') {
            return { status: 'pending', reason: result.reason };
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async createFile(path, content = '') {
        const result = await this.client.fileCreate(path, content);
        
        if (result.type === 'file_created') {
            return result;
        } else if (result.type === 'file_create_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async deleteFile(path) {
        const result = await this.client.fileDelete(path);
        
        if (result.type === 'file_deleted') {
            if (this.currentFile && this.currentFile.path === path) {
                this.currentFile = null;
            }
            return result;
        } else if (result.type === 'file_delete_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'file_delete_pending') {
            return { status: 'pending', reason: result.reason };
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async renameFile(oldPath, newPath) {
        const result = await this.client.fileRename(oldPath, newPath);
        
        if (result.type === 'file_renamed') {
            if (this.currentFile && this.currentFile.path === oldPath) {
                this.currentFile.path = newPath;
            }
            return result;
        } else if (result.type === 'file_rename_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async refreshFileTree() {
        const result = await this.client.directoryList();
        
        if (result.type === 'directory_tree') {
            this.fileTree = result.tree;
            return this.fileTree;
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async runCode(language, code, filePath = null) {
        const result = await this.client.executeCode(language, code, filePath);
        
        if (result.type === 'execution_result') {
            return {
                success: result.success,
                stdout: result.stdout,
                stderr: result.stderr,
                exitCode: result.exit_code,
                duration: result.duration_ms,
                verified: result.verified
            };
        } else if (result.type === 'execution_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async scanFile(filePath) {
        const result = await this.client.securityScan(filePath);
        
        if (result.type === 'security_scan_result') {
            return {
                file: result.file,
                hunterAlerts: result.hunter_alerts,
                alerts: result.alerts,
                staticAnalysis: result.static_analysis,
                riskScore: result.risk_score,
                recommendation: result.recommendation
            };
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async fixIssue(filePath, issue) {
        const result = await this.client.autoFix(filePath, issue);
        
        if (result.type === 'auto_fix_applied') {
            return result;
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    async quarantineFile(filePath) {
        const result = await this.client.autoQuarantine(filePath);
        
        if (result.type === 'file_quarantined') {
            if (this.currentFile && this.currentFile.path === filePath) {
                this.currentFile = null;
            }
            return {
                originalPath: result.original_path,
                quarantinePath: result.quarantine_path,
                verified: result.verified
            };
        } else if (result.type === 'quarantine_blocked') {
            throw new Error(`Blocked: ${result.reason}`);
        } else if (result.type === 'error') {
            throw new Error(result.message);
        }
    }

    markFileModified() {
        if (this.currentFile) {
            this.currentFile.modified = true;
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { IDEWebSocketClient, IDEManager };
}
