class BoardroomRenderer {
  constructor() {
    this.templateCache = {};
  }

  async getTemplate(name) {
    if (this.templateCache[name]) return this.templateCache[name];
    const res = await fetch(`/assets/templates/${name}.html`);
    const text = await res.text();
    this.templateCache[name] = text;
    return text;
  }

  renderTemplate(template, data) {
    return template.replace(/{{(\w+)}}/g, (_, key) => data[key] || '');
  }

  async render() {
    // Fetch data
    const [stakeholders, conversation] = await Promise.all([
      fetch('/assets/data/stakeholders.json').then(r => r.json()),
      fetch('/api/conversation').then(r => r.json())
    ]);
    // Fetch templates
    const [stakeholderTpl, chatMsgTpl] = await Promise.all([
      this.getTemplate('stakeholder'),
      this.getTemplate('chat-message')
    ]);
    // Render stakeholders
    const stakeholderHTML = stakeholders.map(s => this.renderTemplate(stakeholderTpl, s)).join('');
    document.querySelector('.stakeholder-list').innerHTML = stakeholderHTML;
    // Render chat messages
    const chatHTML = conversation.map(msg => {
      // Find emoji for role
      const stakeholder = stakeholders.find(s => s.role === msg.role);
      return this.renderTemplate(chatMsgTpl, {
        ...msg,
        emoji: stakeholder ? stakeholder.emoji : '👤'
      });
    }).join('');
    document.querySelector('.chat-messages').innerHTML = chatHTML;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const renderer = new BoardroomRenderer();
  renderer.render();
});

(function() {
  const sidebar = document.getElementById('membersSidebar');
  const toggleStrip = document.getElementById('sidebarToggleStrip');
  const toggleMembersBtn = document.getElementById('toggleMembersBtn');
  const icon = document.getElementById('sidebarToggleIcon');
  const closeBtn = document.getElementById('sidebarCloseBtn');
  const chatArea = document.getElementById('chatArea');
  let collapsed = false;
  function setCollapsed(state) {
    collapsed = state;
    if (collapsed) {
      sidebar.style.width = '0';
      sidebar.style.minWidth = '0';
      sidebar.style.maxWidth = '0';
      sidebar.style.opacity = '0';
      sidebar.style.pointerEvents = 'none';
      icon.classList.remove('fa-angle-double-left');
      icon.classList.add('fa-angle-double-right');
    } else {
      sidebar.style.width = '320px';
      sidebar.style.minWidth = '320px';
      sidebar.style.maxWidth = '320px';
      sidebar.style.opacity = '1';
      sidebar.style.pointerEvents = '';
      icon.classList.remove('fa-angle-double-right');
      icon.classList.add('fa-angle-double-left');
    }
    // Optionally, force chat area to resize (not strictly needed with flexbox, but for safety)
    chatArea.style.transition = 'flex-basis 0.3s';
  }
  toggleMembersBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    setCollapsed(!collapsed);
  });
  icon.addEventListener('click', function(e) {
    e.stopPropagation();
    setCollapsed(!collapsed);
  });
  closeBtn.addEventListener('click', function() {
    setCollapsed(true);
  });
  // Start expanded
  setCollapsed(false);
})();
