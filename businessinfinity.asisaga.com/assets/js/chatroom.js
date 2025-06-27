// chatroom.js: Dynamic loading and rendering of members and chat messages

// Utility to load a template file and cache it
const templateCache = {};
async function loadTemplate(path) {
  if (templateCache[path]) return templateCache[path];
  const res = await fetch(path);
  const text = await res.text();
  templateCache[path] = text;
  return text;
}

// Simple template rendering: replaces {{var}} with values from data
function renderTemplate(template, data) {
  return template.replace(/{{(\w+)}}/g, (match, key) => {
    return key in data ? data[key] : '';
  });
}

// Support for {{#if ...}} ... {{/if}} and {{#unless ...}} ... {{/unless}}
function renderLogicBlocks(template, data) {
  // #if
  template = template.replace(/{{#if (\w+)}}([\s\S]*?){{\/if}}/g, (m, key, content) => {
    return data[key] ? content : '';
  });
  // #unless
  template = template.replace(/{{#unless (\w+)}}([\s\S]*?){{\/unless}}/g, (m, key, content) => {
    return !data[key] ? content : '';
  });
  return template;
}

async function renderMembers(members, lastMessages, unreadCounts, messages) {
  const membersList = document.getElementById('membersListContainer');
  if (!membersList) return;
  membersList.innerHTML = '';
  const template = await loadTemplate('/assets/templates/chatroom-member-item.html');
  for (const member of members) {
    const lastMsgObj = lastMessages.find(lm => lm.memberId === member.id) || {};
    const unreadObj = unreadCounts.find(u => u.memberId === member.id) || {};
    let lastMessageText = '';
    if (lastMsgObj.lastMessageId) {
      const msg = messages.find(m => m.id === lastMsgObj.lastMessageId);
      lastMessageText = msg ? msg.text : '';
    }
    const badgeClass = member.status === 'online' ? 'chatroom-member-badge-success' :
      member.status === 'away' ? 'chatroom-member-badge-warning' : 'chatroom-member-badge-danger';
    const badgeLabel = member.status === 'online' ? 'Online' : member.status === 'away' ? 'Away' : 'Offline';
    const unreadHtml = unreadObj.unread > 0 ? `<span class=\"chatroom-member-unread\">${unreadObj.unread}</span>` : '';
    const html = renderTemplate(template, {
      avatar: member.avatar,
      name: member.name,
      role: member.role || '',
      lastMessageText,
      badgeClass,
      badgeLabel,
      lastSeen: lastMsgObj.lastSeen || '',
      unreadHtml
    });
    membersList.innerHTML += html;
  }
}

async function renderMessages(messages, members) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;
  chatMessages.innerHTML = '';
  const template = await loadTemplate('/assets/templates/chatroom-message-item.html');
  for (const msg of messages) {
    const isReceived = msg.direction === 'received';
    const sender = members.find(m => m.id === msg.senderId) || {};
    const senderName = sender.name || 'Unknown';
    const senderAvatar = sender.avatar || '';
    const html = renderLogicBlocks(template, {
      isReceived,
      avatar: senderAvatar,
      name: senderName,
      rowClass: isReceived ? 'chatroom-message-row-start' : 'chatroom-message-row-end',
      textClass: isReceived ? 'chatroom-message-text-received' : 'chatroom-message-text-sent',
      metaClass: isReceived ? 'chatroom-message-meta-received' : 'chatroom-message-meta-sent',
      text: msg.text,
      timestamp: msg.timestamp
    });
    chatMessages.innerHTML += renderTemplate(html, {
      avatar: senderAvatar,
      name: senderName,
      text: msg.text,
      timestamp: msg.timestamp,
      rowClass: isReceived ? 'chatroom-message-row-start' : 'chatroom-message-row-end',
      textClass: isReceived ? 'chatroom-message-text-received' : 'chatroom-message-text-sent',
      metaClass: isReceived ? 'chatroom-message-meta-received' : 'chatroom-message-meta-sent'
    });
  }
}

document.addEventListener('DOMContentLoaded', function () {
  Promise.all([
    fetch('/assets/data/members.json').then(res => res.json()),
    fetch('/assets/data/last_messages.json').then(res => res.json()),
    fetch('/assets/data/unread_counts.json').then(res => res.json()),
    fetch('/assets/data/chat.json').then(res => res.json())
  ]).then(([members, lastMessages, unreadCounts, messages]) => {
    renderMembers(members, lastMessages, unreadCounts, messages);
    renderMessages(messages, members);
  });
});
