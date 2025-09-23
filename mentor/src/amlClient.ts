import axios from 'axios';
import { AgentInfo, FineTuneJob } from './types';

export class AMLClient {
  private baseUrl = process.env.AZURE_FUNCTIONS_URL || 'http://localhost:7071/api';
  private apiKey = process.env.AZURE_API_KEY || '';

  private headers() {
    return { 
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async listAgents(): Promise<AgentInfo[]> {
    try {
      const res = await axios.get(`${this.baseUrl}/mentor/agents`, { headers: this.headers() });
      return res.data.agents || [];
    } catch (error) {
      console.error('Error listing agents:', error);
      return [];
    }
  }

  async chatWithAgent(agentId: string, message: string, onChunk: (chunk: string) => void) {
    try {
      const res = await axios.post(`${this.baseUrl}/mentor/chat/${agentId}`, 
        { message }, 
        { headers: this.headers() }
      );

      // For non-streaming response, call onChunk with the full response
      if (res.data.response) {
        onChunk(res.data.response);
      }

      return { text: res.data.response || 'Chat complete.' };
    } catch (error) {
      console.error('Error chatting with agent:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onChunk(`Error: ${errorMessage}`);
      return { text: 'Chat failed.' };
    }
  }

  async fineTuneAgent(agentId: string, datasetId: string): Promise<FineTuneJob> {
    try {
      const res = await axios.post(`${this.baseUrl}/mentor/fine-tune/${agentId}`, 
        { datasetId }, 
        { headers: this.headers() }
      );
      return res.data;
    } catch (error) {
      console.error('Error starting fine-tuning:', error);
      throw error;
    }
  }

  async streamTrainingLogs(jobId: string, onLog: (log: string) => void) {
    try {
      const res = await axios.get(`${this.baseUrl}/mentor/logs/${jobId}`, {
        headers: this.headers()
      });

      if (res.data.logs && Array.isArray(res.data.logs)) {
        res.data.logs.forEach((log: string) => onLog(log));
      }
    } catch (error) {
      console.error('Error streaming logs:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onLog(`Error retrieving logs: ${errorMessage}`);
    }
  }

  async deployAdapter(agentId: string, version: string) {
    try {
      await axios.post(`${this.baseUrl}/mentor/deploy/${agentId}`, 
        { version }, 
        { headers: this.headers() }
      );
    } catch (error) {
      console.error('Error deploying adapter:', error);
      throw error;
    }
  }
}