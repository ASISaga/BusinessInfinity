const HOST = location.origin.replace('businessinfinity', 'cloud.businessinfinity'); // adjust if needed
const BOARDROOM_ID = 'business-infinity';
const CONV_ID = 'default';

class BoardroomChat extends HTMLElement {
  constructor(){ super(); this.interval = null; this.lastKey = null; this.attachShadow({mode:'open'}); }
  connectedCallback(){ this.render(); this.startPolling(); }
  disconnectedCallback(){ clearInterval(this.interval); }
  render(){
    this.shadowRoot.innerHTML = `<div class="panel"><h3>Chat</h3><div id="msgs"></div></div>`;
    const style = document.createElement('style');
    style.textContent = `:host{display:block}.panel{border:1px solid #e5e7eb;border-radius:8px;padding:12px}.msg{padding:8px;border-bottom:1px solid #eee}.meta{color:#6b7280;font-size:12px}`;
    this.shadowRoot.appendChild(style);
  }
  async poll(){
    const qs = new URLSearchParams({ boardroomId: BOARDROOM_ID, conversationId: CONV_ID });
    if (this.lastKey) qs.set('since', this.lastKey);
    const res = await fetch(`${HOST}/messages?${qs}`, { cache: 'no-store' });
    const data = await res.json();
    const msgs = data.messages || [];
    if (!msgs.length) return;
    const list = this.shadowRoot.querySelector('#msgs');
    for (const m of msgs) {
      const div = document.createElement('div');
      div.className = 'msg';
      div.innerHTML = `<div class="meta">${m.senderAgentId} • ${new Date(m.timestamp*1000).toLocaleString()}</div><div>${escapeHtml(JSON.stringify(m.payload))}</div>`;
      list.appendChild(div);
      this.lastKey = `${Math.floor(m.timestamp*1000).toString().padStart(13,'0')}-${m.messageId}`;
    }
  }
  startPolling(){ this.interval = setInterval(()=>this.poll().catch(()=>{}), 5000); this.poll(); }
}
customElements.define('boardroom-chat', BoardroomChat);

class McpDashboard extends HTMLElement {
  constructor(){ super(); this.attachShadow({mode:'open'}); }
  async connectedCallback(){
    const role = this.getAttribute('role') || 'CMO';
    const scope = this.getAttribute('scope') || 'local';
    const res = await fetch(`${HOST}/dashboard?role=${role}&scope=${scope}`);
    const { uiSchema } = await res.json();
    this.render(uiSchema);
  }
  render(schema){
    const panels = (schema.panels||[]).map(p => `
      <div class="panel">
        <h3>${p.title}</h3>
        ${p.actions.map(a => `
          <form data-agent="${a.agentId}" data-action="${a.id}">
            ${Object.entries(a.argsSchema||{}).map(([k,def]) => `
              <label>${k}</label>
              ${def.enum ? `<select name="${k}">${def.enum.map(v=>`<option value="${v}">${v}</option>`).join('')}</select>` : `<input name="${k}" type="text" />`}
            `).join('')}
            <button type="submit">${a.label}</button>
          </form>
        `).join('')}
      </div>`).join('');
    this.shadowRoot.innerHTML = `<div>${panels}</div>`;
    this.shadowRoot.querySelectorAll('form').forEach(f => f.addEventListener('submit', e => this.submit(e)));
  }
  async submit(e){
    e.preventDefault();
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const agentId = form.dataset.agent;
    const action = form.dataset.action;
    await fetch(`${HOST}/action`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        boardroomId: BOARDROOM_ID,
        conversationId: CONV_ID,
        agentId, action, args: data, scope: 'local'
      })
    });
    alert('Queued');
  }
}
customElements.define('mcp-dashboard', McpDashboard);

class AmlDemo extends HTMLElement {
  constructor(){ super(); this.attachShadow({mode:'open'}); }
  connectedCallback(){
    this.shadowRoot.innerHTML = `
      <div class="panel">
        <h3>AML Demo / Training</h3>
        <div class="row">
          <form id="infer">
            <label>Agent ID</label><input name="agentId" value="cmo"/>
            <label>Prompt</label><textarea name="prompt"></textarea>
            <button>Infer</button>
          </form>
          <form id="train">
            <label>Job Name</label><input name="jobName" />
            <label>Model Name</label><input name="modelName" />
            <label>Dataset URI</label><input name="datasetUri" />
            <button>Train</button>
          </form>
        </div>
        <pre id="out"></pre>
      </div>
    `;
    this.shadowRoot.getElementById('infer').addEventListener('submit', e => this.call(e, '/aml/infer'));
    this.shadowRoot.getElementById('train').addEventListener('submit', e => this.call(e, '/aml/train'));
  }
  async call(e, path){
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
    const res = await fetch(`${HOST}${path}`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
    const json = await res.json();
    this.shadowRoot.getElementById('out').textContent = JSON.stringify(json, null, 2);
  }
}
customElements.define('aml-demo', AmlDemo);

function escapeHtml(s){ return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }