"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const amlClient_1 = require("./amlClient");
function activate(context) {
    const amlClient = new amlClient_1.AMLClient();
    // Note: Language Model Chat Provider API has compatibility issues with current VS Code API
    // Focusing on command-based implementation for now
    // Command: List Boardroom Agents
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.listAgents', async () => {
        try {
            const agents = await amlClient.listAgents();
            if (agents.length === 0) {
                vscode.window.showInformationMessage('No agents found. Make sure the Business Infinity backend is running.');
                return;
            }
            const agentList = agents.map(agent => `• ${agent.name} (${agent.id}) - Version: ${agent.loraVersion}`).join('\n');
            const doc = await vscode.workspace.openTextDocument({
                content: `# Business Infinity Agents\n\nAvailable agents:\n\n${agentList}\n\n---\n\nUse Ctrl+Shift+P and search for "Mentor Mode" commands to interact with these agents.`,
                language: 'markdown'
            });
            vscode.window.showTextDocument(doc);
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            vscode.window.showErrorMessage(`Failed to list agents: ${errorMessage}`);
        }
    }));
    // Command: Chat with Agent
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.chatWithAgent', async () => {
        const agentId = await vscode.window.showInputBox({
            prompt: 'Enter Agent ID (e.g., ceo, cfo, cto)',
            placeHolder: 'ceo'
        });
        if (!agentId)
            return;
        const message = await vscode.window.showInputBox({
            prompt: 'Enter your message/question for the agent',
            placeHolder: 'What should our strategic priorities be for Q1?'
        });
        if (!message)
            return;
        const outputChannel = vscode.window.createOutputChannel(`Chat with ${agentId.toUpperCase()}`);
        outputChannel.clear();
        outputChannel.show();
        outputChannel.appendLine(`Chat with ${agentId.toUpperCase()} Agent`);
        outputChannel.appendLine('='.repeat(40));
        outputChannel.appendLine(`You: ${message}`);
        outputChannel.appendLine('');
        outputChannel.appendLine('Agent: [Thinking...]');
        try {
            await amlClient.chatWithAgent(agentId, message, (chunk) => {
                outputChannel.clear();
                outputChannel.appendLine(`Chat with ${agentId.toUpperCase()} Agent`);
                outputChannel.appendLine('='.repeat(40));
                outputChannel.appendLine(`You: ${message}`);
                outputChannel.appendLine('');
                outputChannel.appendLine(`Agent: ${chunk}`);
            });
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            outputChannel.appendLine(`Error: ${errorMessage}`);
        }
    }));
    // Command: Fine Tune Agent LoRA
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.fineTuneAgent', async () => {
        const agentId = await vscode.window.showInputBox({
            prompt: 'Enter Agent ID (e.g., ceo, cfo, cto)',
            placeHolder: 'ceo'
        });
        const datasetId = await vscode.window.showInputBox({
            prompt: 'Enter Dataset ID',
            placeHolder: 'business_scenarios_v1'
        });
        if (agentId && datasetId) {
            try {
                const job = await amlClient.fineTuneAgent(agentId, datasetId);
                vscode.window.showInformationMessage(`Fine-tuning started: Job ${job.jobId}`, 'View Logs')
                    .then(selection => {
                    if (selection === 'View Logs') {
                        vscode.commands.executeCommand('boardroom.viewTrainingLogs');
                    }
                });
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                vscode.window.showErrorMessage(`Failed to start fine-tuning: ${errorMessage}`);
            }
        }
    }));
    // Command: View Training Logs
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.viewTrainingLogs', async () => {
        const jobId = await vscode.window.showInputBox({
            prompt: 'Enter Job ID',
            placeHolder: 'job_ceo_dataset_20231201_123456'
        });
        if (jobId) {
            const outputChannel = vscode.window.createOutputChannel('Mentor Mode Training Logs');
            outputChannel.clear();
            outputChannel.show();
            outputChannel.appendLine(`Training Logs for Job: ${jobId}`);
            outputChannel.appendLine('='.repeat(50));
            try {
                await amlClient.streamTrainingLogs(jobId, log => {
                    outputChannel.appendLine(log);
                });
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                outputChannel.appendLine(`Error: ${errorMessage}`);
            }
        }
    }));
    // Command: Deploy LoRA Adapter
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.deployAdapter', async () => {
        const agentId = await vscode.window.showInputBox({
            prompt: 'Enter Agent ID to deploy',
            placeHolder: 'ceo'
        });
        const version = await vscode.window.showInputBox({
            prompt: 'Enter LoRA Version to deploy',
            placeHolder: 'v1.1.0'
        });
        if (agentId && version) {
            try {
                await amlClient.deployAdapter(agentId, version);
                vscode.window.showInformationMessage(`Adapter deployed for ${agentId} version ${version}`);
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                vscode.window.showErrorMessage(`Failed to deploy adapter: ${errorMessage}`);
            }
        }
    }));
    // Command: Compare LoRA Versions
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.compareVersions', async () => {
        const agentId = await vscode.window.showInputBox({
            prompt: 'Enter Agent ID to compare versions',
            placeHolder: 'ceo'
        });
        if (agentId) {
            const version1 = await vscode.window.showInputBox({
                prompt: 'Enter first version to compare',
                placeHolder: 'v1.0.0'
            });
            const version2 = await vscode.window.showInputBox({
                prompt: 'Enter second version to compare',
                placeHolder: 'v1.1.0'
            });
            if (version1 && version2) {
                // Create a comparison document
                const doc = await vscode.workspace.openTextDocument({
                    content: `# LoRA Version Comparison for ${agentId.toUpperCase()}

## Version ${version1} vs Version ${version2}

This feature will compare the performance of different LoRA versions.
You can test both versions with the same prompts and compare their responses.

### Test Prompts
- Add your test prompts here
- Use the "Chat with Agent" command to test each version
- Document the differences in responses

### Performance Metrics
- Response quality
- Consistency
- Domain-specific accuracy

### Test Results

| Prompt | ${version1} Response | ${version2} Response | Notes |
|--------|---------------------|---------------------|--------|
| Example prompt here | Response 1 | Response 2 | Comparison notes |

---

**Instructions:**
1. Use Ctrl+Shift+P → "Mentor Mode: Chat with Agent" 
2. Test the same prompts with both versions
3. Document results in the table above

Note: Full comparison functionality requires integration with training metrics API.
`,
                    language: 'markdown'
                });
                vscode.window.showTextDocument(doc);
                vscode.window.showInformationMessage(`Comparison document created for ${agentId} ${version1} vs ${version2}`);
            }
        }
    }));
    // Command: Management Command (main entry point)
    context.subscriptions.push(vscode.commands.registerCommand('boardroom.manage', async () => {
        const options = [
            'List Agents',
            'Chat with Agent',
            'Start Fine-Tuning',
            'View Training Logs',
            'Deploy Adapter',
            'Compare Versions'
        ];
        const selection = await vscode.window.showQuickPick(options, {
            placeHolder: 'Select a mentor mode operation'
        });
        switch (selection) {
            case 'List Agents':
                vscode.commands.executeCommand('boardroom.listAgents');
                break;
            case 'Chat with Agent':
                vscode.commands.executeCommand('boardroom.chatWithAgent');
                break;
            case 'Start Fine-Tuning':
                vscode.commands.executeCommand('boardroom.fineTuneAgent');
                break;
            case 'View Training Logs':
                vscode.commands.executeCommand('boardroom.viewTrainingLogs');
                break;
            case 'Deploy Adapter':
                vscode.commands.executeCommand('boardroom.deployAdapter');
                break;
            case 'Compare Versions':
                vscode.commands.executeCommand('boardroom.compareVersions');
                break;
        }
    }));
}
function deactivate() { }
//# sourceMappingURL=extension.js.map