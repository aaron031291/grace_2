// LibrarianService.ts
// This service acts as the "Central Nervous System" for the Librarian.
// It intercepts actions, assigns Cryptographic Keys (Memory DNA), and persists them.
// NOW WITH BACKEND API INTEGRATION!

const API_BASE_URL = 'http://localhost:5371/api/librarian';
const VECTOR_API_URL = 'http://localhost:5001/api/vector';

export interface LifecycleEvent {
    timestamp: string;
    action: string; // e.g., "Created", "Updated", "Promoted", "Renamed"
    actor: string; // e.g., "User", "Agent:Builder"
    description: string;
    previousVersionId?: string;
    snapshot?: any; // Metadata snapshot at this point
}

export interface MemoryDNA {
    artifactId: string; // The Soul (Permanent Root Key)
    versionId: string; // The Body (Current State Hash)
    origin: string; // Agent or User who initiated
    timestamp: string;
    intent: string; // The goal (e.g., "Build Blockchain")
    checksum: string; // Integrity hash
    lifecycle: LifecycleEvent[]; // Structured Log of events
}

export interface LibrarianItem {
    id: string;
    name: string;
    type: 'file' | 'folder';
    dna: MemoryDNA;
    layer: 'lightning' | 'fusion'; // Track which layer this item is in
    ttl?: number; // Time-to-live for Lightning items
}

class LibrarianService {
    private static instance: LibrarianService;

    // Local cache (synced with backend)
    private lightningCache: Map<string, LibrarianItem> = new Map();
    private fusionCache: LibrarianItem[] = [];
    private lastSync: number = 0;

    private activeIntent: string = 'General Interaction';

    private constructor() {
        // Initialize by loading from backend
        this.syncFromBackend();

        // Periodic sync every 5 seconds
        setInterval(() => this.syncFromBackend(), 5000);
    }

    public static getInstance(): LibrarianService {
        if (!LibrarianService.instance) {
            LibrarianService.instance = new LibrarianService();
        }
        return LibrarianService.instance;
    }

    // ========== BACKEND SYNC ==========

    private async syncFromBackend() {
        try {
            // Fetch Lightning items
            const lightningRes = await fetch(`${API_BASE_URL}/lightning`);
            if (lightningRes.ok) {
                const lightningItems: LibrarianItem[] = await lightningRes.json();
                this.lightningCache.clear();
                lightningItems.forEach(item => this.lightningCache.set(item.id, item));
            }

            // Fetch Fusion items
            const fusionRes = await fetch(`${API_BASE_URL}/fusion`);
            if (fusionRes.ok) {
                this.fusionCache = await fusionRes.json();
            }

            this.lastSync = Date.now();
        } catch (error) {
            console.warn('[Librarian] Backend sync failed:', error);
        }
    }

    // ========== DNA GENERATION (Client-Side) ==========

    public generateDNA(origin: string, intent: string, content: string, existingArtifactId?: string, actionType: string = 'Created'): MemoryDNA {
        const timestamp = new Date().toLocaleString();

        // 1. ArtifactID: Deterministic or UUID
        let artifactId = existingArtifactId;
        if (!artifactId) {
            const sourceSignature = this.simpleHash(origin + intent + timestamp);
            artifactId = `ART-${sourceSignature}-${this.generateUUID().substring(0, 8)}`;
        }

        // 2. VersionID: Always new for every state change
        const versionId = `VER-${this.simpleHash(content + timestamp)}`;
        const checksum = this.simpleHash(content);

        // Create the lifecycle event
        const newEvent: LifecycleEvent = {
            timestamp,
            action: actionType,
            actor: origin,
            description: `Version ${versionId} generated via ${actionType}`,
            snapshot: { checksum, intent }
        };

        return {
            artifactId,
            versionId,
            origin,
            timestamp,
            intent: intent || this.activeIntent,
            checksum,
            lifecycle: [newEvent]
        };
    }

    // ========== TRACK ACTION (LIGHTNING) ==========

    public async trackAction(action: string, origin: string, details: string, existingId?: string): Promise<MemoryDNA> {
        // If updating an existing item, fetch its history
        let previousLifecycle: LifecycleEvent[] = [];
        let existingItem: LibrarianItem | undefined;

        if (existingId) {
            existingItem = this.lightningCache.get(existingId) || this.fusionCache.find(i => i.id === existingId);
            if (existingItem) {
                previousLifecycle = existingItem.dna.lifecycle;
            }
        }

        const dna = this.generateDNA(origin, this.activeIntent, details, existingId, existingId ? 'Updated' : 'Created');

        // Merge history
        dna.lifecycle = [...previousLifecycle, ...dna.lifecycle];

        console.log(`[Librarian] ⚡ Action -> Lightning: ${action} | Root: ${dna.artifactId}`);

        // Create/Update the item
        const item: LibrarianItem = {
            id: dna.artifactId,
            name: existingItem ? existingItem.name : `Action-${Date.now()}`,
            type: 'file',
            dna: dna,
            layer: 'lightning',
            ttl: Date.now() + 300000
        };

        // Send to backend
        try {
            const response = await fetch(`${API_BASE_URL}/lightning`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item)
            });

            if (response.ok) {
                // Update local cache
                this.lightningCache.set(dna.artifactId, item);
                console.log('[Librarian] ✅ Synced to backend');
            } else {
                console.error('[Librarian] ❌ Backend sync failed');
            }
        } catch (error) {
            console.error('[Librarian] ❌ Backend error:', error);
            // Still update cache for offline functionality
            this.lightningCache.set(dna.artifactId, item);
        }

        return dna;
    }

    // ========== PROMOTE (LIGHTNING → FUSION) ==========

    public async promote(artifactId: string): Promise<boolean> {
        const item = this.lightningCache.get(artifactId);
        if (!item) {
            console.warn(`[Librarian] ⚠️ Cannot promote ${artifactId}: Not found in Lightning.`);
            return false;
        }

        // ========== GOVERNANCE CHECKS (Client-Side) ==========

        const trustScore = this.getTrustScore(item);
        console.log(`[Librarian] ⚖️ Trust Score: ${trustScore.toFixed(2)}`);

        if (trustScore < 0.7) {
            console.warn(`[Librarian] ❌ Promotion DENIED: Trust score too low (${trustScore.toFixed(2)} < 0.7)`);

            const rejectionEvent: LifecycleEvent = {
                timestamp: new Date().toLocaleString(),
                action: 'PromotionRejected',
                actor: 'GovernanceKernel',
                description: `Rejected: Trust score ${trustScore.toFixed(2)} below threshold`,
                previousVersionId: item.dna.versionId
            };
            item.dna.lifecycle.push(rejectionEvent);

            return false;
        }

        if (this.checkContradictions(item)) {
            console.warn(`[Librarian] ❌ Promotion DENIED: Contradictions detected`);

            const rejectionEvent: LifecycleEvent = {
                timestamp: new Date().toLocaleString(),
                action: 'PromotionRejected',
                actor: 'GovernanceKernel',
                description: 'Rejected: Contradicts existing Fusion artifacts',
                previousVersionId: item.dna.versionId
            };
            item.dna.lifecycle.push(rejectionEvent);

            return false;
        }

        if (this.violatesConstitution(item)) {
            console.warn(`[Librarian] ❌ Promotion DENIED: Constitutional violation`);

            const rejectionEvent: LifecycleEvent = {
                timestamp: new Date().toLocaleString(),
                action: 'PromotionRejected',
                actor: 'GovernanceKernel',
                description: 'Rejected: Violates constitutional policies',
                previousVersionId: item.dna.versionId
            };
            item.dna.lifecycle.push(rejectionEvent);

            return false;
        }

        console.log(`[Librarian] ✅ Governance APPROVED (Trust: ${trustScore.toFixed(2)})`);

        // Log promotion event
        const promotionEvent: LifecycleEvent = {
            timestamp: new Date().toLocaleString(),
            action: 'Promoted',
            actor: 'GovernanceKernel',
            description: `Promoted from Lightning to Fusion (Trust: ${trustScore.toFixed(2)})`,
            previousVersionId: item.dna.versionId,
            snapshot: { trustScore }
        };
        item.dna.lifecycle.push(promotionEvent);

        // Send to backend
        try {
            const response = await fetch(`${API_BASE_URL}/promote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ artifactId })
            });

            if (response.ok) {
                // Update local cache
                this.lightningCache.delete(artifactId);
                item.layer = 'fusion';
                delete item.ttl;
                this.fusionCache.push(item);

                console.log(`[Librarian] 🧱 Promoted to Fusion: ${artifactId}`);
                return true;
            } else {
                console.error('[Librarian] ❌ Backend promotion failed');
                return false;
            }
        } catch (error) {
            console.error('[Librarian] ❌ Backend error:', error);
            return false;
        }
    }

    // ========== GOVERNANCE METHODS ==========

    private getTrustScore(item: LibrarianItem): number {
        let score = 0.5;

        if (item.dna.origin === 'User') {
            score += 0.3;
        } else if (item.dna.origin.startsWith('Agent:')) {
            score += 0.2;
        } else if (item.dna.origin === 'GovernanceKernel') {
            score += 0.3;
        }

        const hasContradictions = this.checkContradictions(item);
        if (!hasContradictions) {
            score += 0.2;
        }

        const validationCount = item.dna.lifecycle.filter(e =>
            e.action === 'Validated' || e.action === 'Promoted' || e.action === 'Created'
        ).length;
        score += Math.min(validationCount * 0.1, 0.3);

        const TRUSTED_INTENTS = ['HealthCheck', 'Audit', 'ModelInitialization', 'FileUpload'];
        if (TRUSTED_INTENTS.includes(item.dna.intent)) {
            score += 0.2;
        }

        return Math.min(score, 1.0);
    }

    private checkContradictions(item: LibrarianItem): boolean {
        const fusionItemsWithSameIntent = this.fusionCache.filter(i =>
            i.dna.intent === item.dna.intent
        );

        if (fusionItemsWithSameIntent.length === 0) {
            return false;
        }

        const checksums = fusionItemsWithSameIntent.map(i => i.dna.checksum);
        const hasDifferentChecksum = !checksums.includes(item.dna.checksum);

        if (hasDifferentChecksum && item.dna.intent !== 'General Interaction') {
            console.log(`[Librarian] ⚠️ Potential contradiction: Same intent "${item.dna.intent}" but different checksum`);
            return false;
        }

        return false;
    }

    private violatesConstitution(item: LibrarianItem): boolean {
        const FORBIDDEN_PATTERNS = [
            /delete.*all/i,
            /rm\s+-rf\s+\//i,
            /DROP\s+TABLE/i,
            /DROP\s+DATABASE/i,
            /format\s+c:/i,
            /sudo\s+rm/i
        ];

        const content = JSON.stringify(item);
        const violatesPattern = FORBIDDEN_PATTERNS.some(pattern => pattern.test(content));

        if (violatesPattern) {
            console.error(`[Librarian] 🚨 CONSTITUTIONAL VIOLATION: Dangerous pattern detected`);
            return true;
        }

        const SENSITIVE_KEYWORDS = ['password', 'api_key', 'secret', 'private_key', 'token'];
        const containsSensitiveData = SENSITIVE_KEYWORDS.some(keyword =>
            content.toLowerCase().includes(keyword)
        );

        if (containsSensitiveData && item.dna.origin !== 'GovernanceKernel') {
            console.warn(`[Librarian] ⚠️ Potential sensitive data detected in ${item.name}`);
        }

        return false;
    }

    // ========== GETTERS ==========

    public setActiveIntent(intent: string) {
        this.activeIntent = intent;
        console.log(`[Librarian] 🧠 Intent Switched: ${intent}`);
    }

    public getMemory(): LibrarianItem[] {
        return [...this.fusionCache, ...Array.from(this.lightningCache.values())];
    }

    public getLightningItems(): LibrarianItem[] {
        return Array.from(this.lightningCache.values());
    }

    public getFusionItems(): LibrarianItem[] {
        return this.fusionCache;
    }

    // ========== RENAME/MOVE OPERATIONS ==========

    public async renameArtifact(artifactId: string, newName: string): Promise<boolean> {
        const item = this.getItemByArtifactId(artifactId);
        if (!item) {
            console.warn(`[Librarian] ⚠️ Cannot rename ${artifactId}: Not found.`);
            return false;
        }

        const oldName = item.name;

        const renameEvent: LifecycleEvent = {
            timestamp: new Date().toLocaleString(),
            action: 'Renamed',
            actor: 'User',
            description: `Renamed from "${oldName}" to "${newName}"`,
            previousVersionId: item.dna.versionId
        };

        item.dna.lifecycle.push(renameEvent);
        item.name = newName;

        // Sync to backend
        try {
            await fetch(`${API_BASE_URL}/rename`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ artifactId, newName })
            });
        } catch (error) {
            console.error('[Librarian] ❌ Rename sync failed:', error);
        }

        console.log(`[Librarian] 📝 Renamed: ${oldName} → ${newName} (Root: ${artifactId})`);
        return true;
    }

    public async moveArtifact(artifactId: string, newPath: string): Promise<boolean> {
        const item = this.getItemByArtifactId(artifactId);
        if (!item) {
            console.warn(`[Librarian] ⚠️ Cannot move ${artifactId}: Not found.`);
            return false;
        }

        const moveEvent: LifecycleEvent = {
            timestamp: new Date().toLocaleString(),
            action: 'Moved',
            actor: 'User',
            description: `Moved to path: ${newPath}`,
            previousVersionId: item.dna.versionId,
            snapshot: { newPath }
        };

        item.dna.lifecycle.push(moveEvent);

        console.log(`[Librarian] 📦 Moved: ${item.name} to ${newPath} (Root: ${artifactId})`);
        return true;
    }

    // ========== VECTOR LAYER (SEMANTIC SEARCH) ==========

    public async rebuildVectorIndex(): Promise<boolean> {
        try {
            const response = await fetch(`${VECTOR_API_URL}/index`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });

            if (response.ok) {
                const result = await response.json();
                console.log(`[Librarian] 🧠 Vector index rebuilt: ${result.indexed_count} artifacts`);
                return true;
            }
            return false;
        } catch (error) {
            console.error('[Librarian] ❌ Vector index rebuild failed:', error);
            return false;
        }
    }

    public async semanticSearch(query: string, topK: number = 5): Promise<LibrarianItem[]> {
        try {
            const response = await fetch(`${VECTOR_API_URL}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, topK })
            });

            if (response.ok) {
                const results = await response.json();
                console.log(`[Librarian] 🔍 Semantic search: "${query}" → ${results.length} results`);

                // Map results to LibrarianItems
                const items: LibrarianItem[] = [];
                for (const result of results) {
                    const item = this.fusionCache.find(i => i.id === result.artifactId);
                    if (item) {
                        items.push({
                            ...item,
                            // Add similarity score to the item (for UI display)
                            similarity: result.similarity
                        } as any);
                    }
                }

                return items;
            }
            return [];
        } catch (error) {
            console.error('[Librarian] ❌ Semantic search failed:', error);
            return [];
        }
    }

    public async embedArtifact(artifactId: string, content: string): Promise<boolean> {
        try {
            const response = await fetch(`${VECTOR_API_URL}/embed`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ artifactId, content })
            });

            if (response.ok) {
                console.log(`[Librarian] ➕ Embedded artifact: ${artifactId}`);
                return true;
            }
            return false;
        } catch (error) {
            console.error('[Librarian] ❌ Embedding failed:', error);
            return false;
        }
    }

    // ========== HELPERS ==========

    private getItemByArtifactId(artifactId: string): LibrarianItem | undefined {
        const lightningItem = this.lightningCache.get(artifactId);
        if (lightningItem) return lightningItem;

        return this.fusionCache.find(item => item.id === artifactId);
    }

    private simpleHash(str: string): string {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16);
    }

    private generateUUID(): string {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

export const librarian = LibrarianService.getInstance();
