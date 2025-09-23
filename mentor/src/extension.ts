import * as vscode from 'vscode';
import { AMLClient } from './amlClient';

export function activate(context: vscode.ExtensionContext) {
  const amlClient = new AMLClient();

  const provider: vscode.LanguageModelChatProvider = {
    async provideLanguageModelChatInformation(token) {
      const agents = await amlClient.listAgents();
      return agents.map(agent => ({
        id: agent.id,
        name: agent.name,
        family: 'custom-lora',
        version: agent.loraVersion,
        capabilities: ['chat', 'fine-tune'],
        maxTokens: 4096
      }));
    },

    async provideLanguageModelChatResponse(request, context, token) {
      const agentId = request.model.id;
      const message = request.prompt;

      return amlClient.chatWithAgent(agentId, message, chunk => {
        context.sendPartialResponse(chunk);
      });
    },

    async provideTokenCount(model, text, token) {
      return text.split(/\s+/).length;
    }
  };

  context.subscriptions.push(
    vscode.languageModelChat.registerLanguageModelChatProvider('boardroom-llm', provider)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('boardroom.fineTuneAgent', async () => {
      const agentId = await vscode.window.showInputBox({ prompt: 'Agent ID' });
      const datasetId = await vscode.window.showInputBox({ prompt: 'Dataset ID' });
      if (agentId && datasetId) {
        const job = await amlClient.fineTuneAgent(agentId, datasetId);
        vscode.window.showInformationMessage(`Fine-tuning started: Job ${job.jobId}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('boardroom.viewTrainingLogs', async () => {
      const jobId = await vscode.window.showInputBox({ prompt: 'Job ID' });
      if (jobId) {
        const outputChannel = vscode.window.createOutputChannel('Training Logs');
        amlClient.streamTrainingLogs(jobId, log => {
          outputChannel.appendLine(log);
        });
        outputChannel.show();
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('boardroom.deployAdapter', async () => {
      const agentId = await vscode.window.showInputBox({ prompt: 'Agent ID' });
      const version = await vscode.window.showInputBox({ prompt: 'LoRA Version' });
      if (agentId && version) {
        await amlClient.deployAdapter(agentId, version);
        vscode.window.showInformationMessage(`Adapter deployed for ${agentId} version ${version}`);
      }
    })
  );
}

export function deactivate() {}