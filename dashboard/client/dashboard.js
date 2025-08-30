class BoardroomDashboard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.manifest = null;
    this.selectedRole = this.getAttribute('role') || 'ALL';
  }

  async connectedCallback() {
    const manifestUrl = this.getAttribute('manifest-url');
    if (!manifestUrl) return this._renderError('No manifest-url attribute provided.');
    try {
      const res = await fetch(manifestUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.manifest = await res.json();
      this._render();
    } catch (e) {
      this._renderError(`Failed to load manifest: ${e.message}`);
    }
  }

  _render() {
    const styleLink = `<link rel="stylesheet" href="styles.css">`;
    const roles = this._availableRoles();
    const roleSelect = `
      <div class="header">
        <strong>Role:</strong>
        <select class="select" id="roleSelect">
          <option value="ALL"${this.selectedRole==='ALL'?' selected':''}>ALL</option>
          ${roles.map(r => `<option value="${r}"${this.selectedRole===r?' selected':''}>${r}</option>`).join('')}
        </select>
        <span style="margin-left:auto"><strong>${this.manifest.title}</strong></span>
      </div>
    `;

    const panels = this._filteredPanels().map(p => this._panelHtml(p)).join('');

    this.shadowRoot.innerHTML = `
      ${styleLink}
      ${roleSelect}
      <div class="dashboard">${panels}</div>
    `;

    this.shadowRoot.getElementById('roleSelect').addEventListener('change', (e) => {
      this.selectedRole = e.target.value;
      this._render();
    });

    this._bindActions();
  }

  _availableRoles() {
    const set = new Set(this.manifest.panels.map(p => p.role));
    return Array.from(set);
  }

  _filteredPanels() {
    const all = this.manifest.panels;
    if (this.selectedRole === 'ALL') return all;
    return all.filter(p => p.role === this.selectedRole);
  }

  _panelHtml(panel) {
    const res = this.manifest.uiResources.find(r => r.uri === panel.uri);
    const payload = res ? res.payload : '<em>No content</em>';
    const actions = (panel.actions || []).map(a => {
      const data = encodeURIComponent(JSON.stringify({ panelUri: panel.uri, actionId: a.id }));
      return `<button data-bind="${data}">${a.label}</button>`;
    }).join('');
    return `
      <div class="panel">
        <h3>${panel.title} <span style="color:#64748b;font-weight:400">(${panel.role})</span></h3>
        <div class="payload">${payload}</div>
        <div class="actions">${actions}</div>
      </div>
    `;
  }

  _bindActions() {
    this.shadowRoot.querySelectorAll('button[data-bind]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const payload = JSON.parse(decodeURIComponent(e.currentTarget.getAttribute('data-bind')));
        const binding = this.manifest.actionBindings.find(b => b.actionId === payload.actionId);
        if (!binding) return alert('No binding for action.');
        const params = await this._collectParams(binding.paramsSchema);
        try {
          const res = await fetch('/api/mcp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', id: Math.random().toString(36).slice(2,8), method: binding.mcpMethod, params })
          });
          const data = await res.json();
          if (data.error) throw new Error(data.error.message);
          alert(`${binding.mcpMethod} OK:\n${JSON.stringify(data.result, null, 2)}`);
        } catch (err) {
          alert(`Error: ${err.message}`);
        }
      });
    });
  }

  async _collectParams(schema) {
    const props = (schema && schema.properties) ? schema.properties : {};
    const required = (schema && schema.required) ? schema.required : [];
    const values = {};
    for (const key of Object.keys(props)) {
      const type = props[key].type || 'string';
      let val = window.prompt(`Enter ${key}${required.includes(key) ? ' *' : ''}:`);
      if (val === null) throw new Error('Cancelled');
      if (type === 'number' || type === 'integer') {
        const num = Number(val);
        if (Number.isNaN(num)) throw new Error(`Invalid number for ${key}`);
        values[key] = num;
      } else {
        values[key] = val;
      }
    }
    return values;
    }
  
  _renderError(msg) {
    this.shadowRoot.innerHTML = `<link rel="stylesheet" href="styles.css"><div class="header"><span style="color:#dc2626">${msg}</span></div>`;
  }
}

customElements.define('boardroom-dashboard', BoardroomDashboard);