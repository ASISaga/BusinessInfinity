// chatroom.js: Dynamic loading and rendering of members and chat messages

document.addEventListener('DOMContentLoaded', function () {
  // Load and render members
  fetch('/data/members.json')
    .then(response => response.json())
    .then(members => renderMembers(members));

  // Load and render chat messages
  fetch('/data/chat.json')
    .then(response => response.json())
    .then(messages => renderMessages(messages));
});

function renderMembers(members) {
  const membersList = document.getElementById('membersListContainer');
  if (!membersList) return;
  membersList.innerHTML = '';
  members.forEach(member => {
    const badgeClass = member.status === 'online' ? 'chatroom-member-badge-success' :
      member.status === 'away' ? 'chatroom-member-badge-warning' : 'chatroom-member-badge-danger';
    const badgeLabel = member.status === 'online' ? 'Online' : member.status === 'away' ? 'Away' : 'Offline';
    membersList.innerHTML += `
      <li class="chatroom-member-item" role="listitem">
        <a href="#" class="chatroom-member-link">
          <div class="chatroom-member-row">
            <div class="chatroom-member-avatar-wrapper">
              <img src="${member.avatar}" alt="Avatar of ${member.name}" class="chatroom-member-avatar">
              <span class="chatroom-member-badge ${badgeClass}" aria-label="${badgeLabel}"></span>
            </div>
            <div class="chatroom-member-info">
              <p class="chatroom-member-name">${member.name}</p>
              <p class="chatroom-member-message">${member.lastMessage}</p>
            </div>
          </div>
          <div class="chatroom-member-meta">
            <p class="chatroom-member-time">${member.lastSeen}</p>
            ${member.unread > 0 ? `<span class="chatroom-member-unread">${member.unread}</span>` : ''}
          </div>
        </a>
      </li>
    `;
  });
}

function renderMessages(messages) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;
  chatMessages.innerHTML = '';
  messages.forEach(msg => {
    const isReceived = msg.direction === 'received';
    chatMessages.innerHTML += `
      <article class="chatroom-message-row ${isReceived ? 'chatroom-message-row-start' : 'chatroom-message-row-end'}">
        ${isReceived ? `<img src="${msg.avatar}" alt="Avatar of ${msg.senderName}" class="chatroom-message-avatar">` : ''}
        <div class="chatroom-message-content">
          <p class="chatroom-message-text ${isReceived ? 'chatroom-message-text-received' : 'chatroom-message-text-sent'}">${msg.text}</p>
          <p class="chatroom-message-meta ${isReceived ? 'chatroom-message-meta-received' : 'chatroom-message-meta-sent'}">${msg.timestamp}</p>
        </div>
        ${!isReceived ? `<img src="${msg.avatar}" alt="Avatar of ${msg.senderName}" class="chatroom-message-avatar">` : ''}
      </article>
    `;
  });
}
