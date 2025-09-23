"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AMLClient = void 0;
const axios_1 = __importDefault(require("axios"));
class AMLClient {
    constructor() {
        this.baseUrl = process.env.AZURE_FUNCTIONS_URL || 'http://localhost:7071/api';
        this.apiKey = process.env.AZURE_API_KEY || '';
    }
    headers() {
        return {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    async listAgents() {
        try {
            const res = await axios_1.default.get(`${this.baseUrl}/mentor/agents`, { headers: this.headers() });
            return res.data.agents || [];
        }
        catch (error) {
            console.error('Error listing agents:', error);
            return [];
        }
    }
    async chatWithAgent(agentId, message, onChunk) {
        try {
            const res = await axios_1.default.post(`${this.baseUrl}/mentor/chat/${agentId}`, { message }, { headers: this.headers() });
            // For non-streaming response, call onChunk with the full response
            if (res.data.response) {
                onChunk(res.data.response);
            }
            return { text: res.data.response || 'Chat complete.' };
        }
        catch (error) {
            console.error('Error chatting with agent:', error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            onChunk(`Error: ${errorMessage}`);
            return { text: 'Chat failed.' };
        }
    }
    async fineTuneAgent(agentId, datasetId) {
        try {
            const res = await axios_1.default.post(`${this.baseUrl}/mentor/fine-tune/${agentId}`, { datasetId }, { headers: this.headers() });
            return res.data;
        }
        catch (error) {
            console.error('Error starting fine-tuning:', error);
            throw error;
        }
    }
    async streamTrainingLogs(jobId, onLog) {
        try {
            const res = await axios_1.default.get(`${this.baseUrl}/mentor/logs/${jobId}`, {
                headers: this.headers()
            });
            if (res.data.logs && Array.isArray(res.data.logs)) {
                res.data.logs.forEach((log) => onLog(log));
            }
        }
        catch (error) {
            console.error('Error streaming logs:', error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            onLog(`Error retrieving logs: ${errorMessage}`);
        }
    }
    async deployAdapter(agentId, version) {
        try {
            await axios_1.default.post(`${this.baseUrl}/mentor/deploy/${agentId}`, { version }, { headers: this.headers() });
        }
        catch (error) {
            console.error('Error deploying adapter:', error);
            throw error;
        }
    }
}
exports.AMLClient = AMLClient;
//# sourceMappingURL=amlClient.js.map