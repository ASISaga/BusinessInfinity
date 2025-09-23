# Business Infinity Mentor Mode - VS Code Extension

This VS Code extension provides a developer-focused interface for managing and fine-tuning Business Infinity AI agents through the mentor mode system.

## Features

- **Language Model Chat Integration**: Chat with Business Infinity agents directly in VS Code
- **Agent Management**: List, select, and interact with CEO, CFO, CTO, Founder, and Investor agents
- **Fine-Tuning Control**: Start LoRA fine-tuning jobs with custom datasets
- **Training Monitoring**: Real-time training logs streaming in VS Code output panel
- **Version Management**: Deploy and compare different LoRA adapter versions
- **Command Palette Integration**: All functions accessible via VS Code command palette

## Installation & Setup

### Prerequisites
- VS Code 1.93.0 or higher
- Node.js 18.x or higher
- TypeScript 5.2.0 or higher
- Business Infinity backend running with mentor mode enabled

### Build Instructions

1. **Install Dependencies**:
   ```bash
   cd mentor
   npm install
   ```

2. **Compile TypeScript**:
   ```bash
   npm run compile
   ```

3. **Package Extension** (optional):
   ```bash
   npm run package
   ```
   This creates a `.vsix` file that can be installed in VS Code.

4. **Development Mode**:
   ```bash
   npm run watch
   ```
   Auto-compiles TypeScript files on changes.

### Configuration

Configure the extension in VS Code settings:

```json
{
  "mentorMode.azureFunctionsUrl": "http://localhost:7071/api",
  "mentorMode.apiKey": "your-api-key-if-required"
}
```

## Usage

### Available Commands

Access via Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`):

- **Mentor Mode: Manage Mentor Mode** - Quick picker for all operations
- **Mentor Mode: List Business Agents** - View available agents and versions
- **Mentor Mode: Fine Tune Agent LoRA** - Start training with custom datasets
- **Mentor Mode: View Training Logs** - Stream training logs to output panel
- **Mentor Mode: Deploy LoRA Adapter** - Deploy trained models to production
- **Mentor Mode: Compare LoRA Versions** - Side-by-side version comparison

### Language Model Chat Provider

The extension registers as a Language Model Chat Provider, allowing you to:

1. Open the Chat view in VS Code
2. Select "Business Infinity Agents" as the model family
3. Choose specific agents (CEO, CFO, CTO, etc.)
4. Chat directly with agents in a sandboxed environment

### Workflow Examples

**1. Test Agent Responses**:
- Use the chat provider to send prompts to different agents
- Compare responses across CEO, CFO, CTO perspectives
- Validate domain-specific knowledge and reasoning

**2. Fine-Tune Agent Behavior**:
- Run `Mentor Mode: Fine Tune Agent LoRA` 
- Provide dataset ID and select target agent
- Monitor progress with `View Training Logs`
- Deploy when satisfied with results

**3. Version Management**:
- Use `Compare LoRA Versions` to evaluate improvements
- Deploy new versions with `Deploy LoRA Adapter`
- Rollback if needed through the web interface

## API Integration

The extension connects to the Business Infinity mentor mode backend:

- `GET /mentor/agents` - List available agents
- `POST /mentor/chat/{agent_id}` - Chat with specific agent  
- `POST /mentor/fine-tune/{agent_id}` - Start training job
- `GET /mentor/logs/{job_id}` - Get training logs
- `POST /mentor/deploy/{agent_id}` - Deploy adapter

## Development

### Project Structure
```
mentor/
├── src/
│   ├── extension.ts      # Main extension entry point
│   ├── amlClient.ts      # API client for backend
│   └── types.ts          # TypeScript type definitions
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/ASISaga/BusinessInfinity.git
cd BusinessInfinity/mentor

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch
```

### Testing

```bash
# Run linting
npm run lint

# Run tests (when available)
npm test
```

## Troubleshooting

**Extension not activating**: 
- Check VS Code version compatibility (1.93.0+)
- Ensure TypeScript compilation succeeded

**API connection issues**:
- Verify `mentorMode.azureFunctionsUrl` setting
- Ensure Business Infinity backend is running
- Check API key configuration if authentication required

**Command not found**:
- Reload VS Code window after installation
- Check command palette for "Mentor Mode:" prefix

## Contributing

1. Make changes to TypeScript files in `src/`
2. Run `npm run compile` to build
3. Test in VS Code development host
4. Submit PR with both source and compiled changes

## License

MIT License - see repository root for details.

---

**Note**: This extension is part of the Business Infinity project and requires the mentor mode backend to be running for full functionality.