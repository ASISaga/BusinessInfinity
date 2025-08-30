class BoardroomDashboard extends HTMLElement {
  async connectedCallback() {
    const manifestUrl = this.getAttribute('manifest-url');
    const roleFilter = this.getAttribute('role');

    const res = await fetch(manifestUrl);
    const manifest = await res.json();

    // Filter panels by role if provided
    let panels = manifest.panels;
    if (roleFilter) {
      panels = panels.filter(p => p.role.toLowerCase() === roleFilter.toLowerCase());
    }

    // Group by role
    const roles = {};
    panels.forEach(panel => {
      if (!roles[panel.role]) roles[panel.role] = {};
      roles[panel.role][panel.scope || 'default'] = panel;
    });

    this.render(roles);
  }

  render(roles) {
    const container = document.createElement('div');
    container.className = 'dashboard';

    Object.keys(roles).forEach(role => {
      const roleContainer = document.createElement('div');

      // Header with scope toggle
      const header = document.createElement('div');
      header.className = 'role-header';

      const title = document.createElement('h2');
      title.textContent = role;
      header.appendChild(title);

      const toggle = document.createElement('div');
      toggle.className = 'scope-toggle';

      const scopes = Object.keys(roles[role]);
      scopes.forEach(scope => {
        const btn = document.createElement('button');
        btn.textContent = scope.charAt(0).toUpperCase() + scope.slice(1);
        btn.addEventListener('click', () => {
          toggle.querySelectorAll('button').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          this.renderPanel(roleContainer, roles[role][scope]);
        });
        toggle.appendChild(btn);
      });

      header.appendChild(toggle);
      roleContainer.appendChild(header);

      // Default to first scope
      const defaultScope = scopes[0];
      this.renderPanel(roleContainer, roles[role][defaultScope]);
      toggle.querySelector('button').classList.add('active');

      container.appendChild(roleContainer);
    });

    this.innerHTML = '';
    this.appendChild(container);
  }

  renderPanel(container, panel) {
    // Remove old panel
    container.querySelectorAll('.panel').forEach(p => p.remove());

    const panelEl = document.createElement('div');
    panelEl.className = 'panel';

    const h3 = document.createElement('h3');
    h3.textContent = panel.title;
    panelEl.appendChild(h3);

    const actionsEl = document.createElement('div');
    actionsEl.className = 'actions';

    panel.actions.forEach(action => {
      const btn = document.createElement('button');
      btn.textContent = action.label;
      btn.addEventListener('click', () => this.triggerAction(action.id));
      actionsEl.appendChild(btn);
    });

    panelEl.appendChild(actionsEl);
    container.appendChild(panelEl);
  }

  async triggerAction(actionId) {
    try {
      const res = await fetch(`/mcp/${actionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      alert(`Action ${actionId} completed: ${JSON.stringify(data)}`);
    } catch (err) {
      console.error(err);
      alert(`Error executing ${actionId}`);
    }
  }
}

customElements.define('boardroom-dashboard', BoardroomDashboard);