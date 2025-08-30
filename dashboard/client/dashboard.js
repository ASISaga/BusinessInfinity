class BoardroomDashboard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  async connectedCallback() {
    const manifestUrl = this.getAttribute('manifest-url');
    if (!manifestUrl) {
      this.renderError('No manifest URL provided.');
      return;
    }

    try {
      const res = await fetch(manifestUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.manifest = await res.json();
      this.render();
    } catch (err) {
      this.renderError(`Failed to load manifest: ${err.message}`);
    }
  }

  render() {
    const styleLink = `<link rel="stylesheet" href="styles.css">`;
    const panels = this.manifest.uiResources?.map(panel => `
      <div class="panel">
        <h2>${panel.title || 'Untitled Panel'}</h2>
        <div class="content">${panel.payload || ''}</div>
        ${this.renderActions(panel.actions)}
      </div>
    `).join('') || '';

    this.shadowRoot.innerHTML = `
      ${styleLink}
      <div class="dashboard">
        ${panels}
      </div>
    `;

    this.bindActions();
  }

  renderActions(actions = []) {
    if (!actions.length) return '';
    return `
      <div class="actions">
        ${actions.map(a => `<button data-action='${JSON.stringify(a)}'>${a.label}</button>`).join('')}
      </div>
    `;
  }

  bindActions() {
    this.shadowRoot.querySelectorAll('button[data-action]').forEach(btn => {
      btn.addEventListener('click', async e => {
        const action = JSON.parse(e.target.dataset.action);
        await this.callMCP(action);
      });
    });
  }

  async callMCP(action) {
    try {
      const res = await fetch('/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: action.method,
          params: action.params || {}
        })
      });
      const result = await res.json();
      console.log('MCP result:', result);
      alert(`Action "${action.label}" executed.`);
    } catch (err) {
      console.error(err);
      alert(`Failed to execute action: ${err.message}`);
    }
  }

  renderError(msg) {
    this.shadowRoot.innerHTML = `
      <style>p { color: red; font-family: sans-serif; }</style>
      <p>${msg}</p>
    `;
  }
}

customElements.define('boardroom-dashboard', BoardroomDashboard);