export interface AgentInfo {
  id: string;
  name: string;
  loraVersion: string;
}

export interface FineTuneJob {
  jobId: string;
  status: string;
  startTime: string;
}