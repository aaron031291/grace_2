export interface MultimodalInput {
  type: 'text' | 'voice' | 'file';
  content: string;
  metadata?: {
    fileName?: string;
    fileSize?: number;
    fileType?: string;
    transcription?: string;
    duration?: number;
    language?: string;
    timestamp\?: Date;\n    imageData\?: string; // Base64 encoded image data
  };
}

export interface InputProcessingResult {
  success: boolean;
  processedInput?: MultimodalInput;
  error?: string;
  requiresConfirmation?: boolean;
}

export class MultimodalInputService {
  private static instance: MultimodalInputService;
  private processingQueue: MultimodalInput[] = [];
  private isProcessing = false;

  private constructor() {}

  static getInstance(): MultimodalInputService {
    if (!MultimodalInputService.instance) {
      MultimodalInputService.instance = new MultimodalInputService();
    }
    return MultimodalInputService.instance;
  }

  /**
   * Process text input
   */
  async processTextInput(text: string): Promise<InputProcessingResult> {
    try {
      const input: MultimodalInput = {
        type: 'text',
        content: text.trim(),
        metadata: {
          timestamp: new Date()
        }
      };

      // Basic validation
      if (!text.trim()) {
        return {
          success: false,
          error: 'Text input cannot be empty'
        };
      }

      return {
        success: true,
        processedInput: input
      };
    } catch (error) {
      return {
        success: false,
        error: `Text processing failed: ${error}`
      };
    }
  }

  /**
   * Process voice input (transcription)
   */
  async processVoiceInput(transcript: string, metadata?: any): Promise<InputProcessingResult> {
    try {
      const input: MultimodalInput = {
        type: 'voice',
        content: transcript.trim(),
        metadata: {
          transcription: transcript,
          language: metadata?.language || 'en',
          duration: metadata?.duration,
          timestamp: new Date()
        }
      };

      // Validate transcription
      if (!transcript.trim()) {
        return {
          success: false,
          error: 'Voice transcription is empty'
        };
      }

      return {
        success: true,
        processedInput: input
      };
    } catch (error) {
      return {
        success: false,
        error: `Voice processing failed: ${error}`
      };
    }
  }

  /**
   * Process file input
   */
  async processFileInput(file: File): Promise<InputProcessingResult> {
    try {
      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        return {
          success: false,
          error: 'File size exceeds 10MB limit',
          requiresConfirmation: true
        };
      }

      // Check file type
      const allowedTypes = [
        'text/plain',
        'text/markdown',
        'application/pdf',
        'application/json',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'audio/mpeg',
        'audio/wav',
        'audio/webm',
        'video/mp4',
        'video/webm'
      ];

      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(txt|md|pdf|json|jpg|jpeg|png|gif|webp|mp3|wav|webm|mp4)$/i)) {
        return {
          success: false,
          error: 'Unsupported file type',
          requiresConfirmation: true
        };
      }

      // For now, create a placeholder content
      // In a real implementation, this would process the file
      const input: MultimodalInput = {
        type: 'file',
        content: `[File: ${file.name}]`,
        metadata: {
          fileName: file.name,
          fileSize: file.size,
          fileType: file.type,
          timestamp: new Date()
        }
      };

      return {
        success: true,
        processedInput: input
      };
    } catch (error) {
      return {
        success: false,
        error: `File processing failed: ${error}`
      };
    }
  }

  /**
   * Combine multiple inputs into a single multimodal message
   */
  async combineInputs(inputs: MultimodalInput[]): Promise<MultimodalInput> {
    const combinedContent = inputs.map(input => {
      switch (input.type) {
        case 'text':
          return input.content;
        case 'voice':
          return `[Voice: ${input.content}]`;
        case 'file':
          return input.content;
        default:
          return input.content;
      }
    }).join(' ');

    return {
      type: 'text', // Combined inputs are treated as text
      content: combinedContent,
      metadata: {
        timestamp: new Date(),
        combinedInputs: inputs.length,
        inputTypes: inputs.map(i => i.type)
      }
    };
  }

  /**
   * Send processed input to backend
   */
  async sendToBackend(input: MultimodalInput, sessionId: string, userId: string = 'user'): Promise<any> {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input.content,
          session_id: sessionId,
          user_id: userId,
          multimodal: true,
          input_type: input.type,
          metadata: input.metadata
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to send to backend: ${error}`);
    }
  }

  /**
   * Process input through the complete pipeline
   */
  async processInput(
    input: MultimodalInput,
    sessionId: string,
    userId: string = 'user'
  ): Promise<InputProcessingResult> {
    try {
      // Add to processing queue
      this.processingQueue.push(input);

      // Process if not already processing
      if (!this.isProcessing) {
        await this.processQueue(sessionId, userId);
      }

      return {
        success: true,
        processedInput: input
      };
    } catch (error) {
      return {
        success: false,
        error: `Processing failed: ${error}`
      };
    }
  }

  /**
   * Process the input queue
   */
  private async processQueue(sessionId: string, userId: string): Promise<void> {
    if (this.isProcessing || this.processingQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    try {
      while (this.processingQueue.length > 0) {
        const input = this.processingQueue.shift()!;
        await this.sendToBackend(input, sessionId, userId);
      }
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Get current processing status
   */
  getProcessingStatus() {
    return {
      isProcessing: this.isProcessing,
      queueLength: this.processingQueue.length
    };
  }
}

// Export singleton instance
export const multimodalInputService = MultimodalInputService.getInstance();
