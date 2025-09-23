import axios from 'axios';
import { AgentInfo, FineTuneJob } from './types';

export class AMLClient {
  private baseUrl = process.env.AZURE_FUNCTIONS_URL || '';
  private apiKey = process.env.AZURE_API_KEY || '';

  private headers() {
    return { 'Authorization': `Bearer ${this.apiKey}` };
  }

  async listAgents(): Promise<AgentInfo[]> {
    const res = await axios.get(`${this.baseUrl}/agents`, { headers: this.headers() });
    return res.data;
  }

  async chatWithAgent(agentId: string, message: string, onChunk: (chunk: string) => void) {
    const res = await axios.post(`${this.baseUrl}/chat/${agentId}`, { message }, {
      headers: this.headers(),
      responseType: 'stream'
    });

    res.data.on('data', (chunk: Buffer) => {
      onChunk(chunk.toString());
    });

    return { text: 'Chat complete.' };
  }

  async fineTuneAgent(agentId: string, datasetId: string): Promise<FineTuneJob> {
    const res = await axios.post(`${this.baseUrl}/fine-tune/${agentId}`, { datasetId }, { headers: this.headers() });
    return res.data;
  }

  async streamTrainingLogs(jobId: string, onLog: (log: string) => void) {
    const res = await axios.get(`${this.baseUrl}/logs/${jobId}`, {
      headers: this.headers(),
      responseType: 'stream'
    });

    res.data.on('data', (chunk: Buffer) => {
      onLog(chunk.toString());
    });
  }

  async deployAdapter(agentId: string, version: string) {
    await axios.post(`${this.baseUrl}/deploy/${agentId}`, { version }, { headers: this.headers() });
  }
}