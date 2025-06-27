import TemplateUtils from './template-utils.js';

class MessagesRenderer {
  constructor(chatMessagesId) {
    this.chatMessages = document.getElementById(chatMessagesId);
  }

  async render(messages, members) {
    if (!this.chatMessages) return;
    this.chatMessages.innerHTML = '';
    const template = await TemplateUtils.loadTemplate('/assets/templates/chatroom-message-item.html');
    for (const msg of messages) {
      const isReceived = msg.direction === 'received';
      const sender = members.find(m => m.id === msg.senderId) || {};
      const senderName = sender.name || 'Unknown';
      const senderAvatar = sender.avatar || '';
      const senderRole = sender.role || '';
      const html = TemplateUtils.renderLogicBlocks(template, {
        isReceived,
        avatar: senderAvatar,
        name: senderName,
        role: senderRole,
        rowClass: isReceived ? 'chatroom-message-row-start' : 'chatroom-message-row-end',
        textClass: isReceived ? 'chatroom-message-text-received' : 'chatroom-message-text-sent',
        metaClass: isReceived ? 'chatroom-message-meta-received' : 'chatroom-message-meta-sent',
        text: msg.text,
        timestamp: msg.timestamp
      });
      this.chatMessages.innerHTML += TemplateUtils.renderTemplate(html, {
        avatar: senderAvatar,
        name: senderName,
        role: senderRole,
        text: msg.text,
        timestamp: msg.timestamp,
        rowClass: isReceived ? 'chatroom-message-row-start' : 'chatroom-message-row-end',
        textClass: isReceived ? 'chatroom-message-text-received' : 'chatroom-message-text-sent',
        metaClass: isReceived ? 'chatroom-message-meta-received' : 'chatroom-message-meta-sent'
      });
    }
  }
}

export default MessagesRenderer;
