// State
let currentTab = 'chat';
let selectedDate = new Date(); 

// Init
window.addEventListener('pywebviewready', function() {
    console.log("PyWebView Ready");
    addMessage('AI', 'System Ready.');
    refreshCalendar();
    loadDashboard();
});

// Calendar Logic
let calViewDate = new Date(); 

function changeMonth(delta) {
    calViewDate.setMonth(calViewDate.getMonth() + delta);
    refreshCalendar();
}

function refreshCalendar() {
    const year = calViewDate.getFullYear();
    const month = calViewDate.getMonth();
    
    // Update Header
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const elHeader = document.getElementById('cal-month-year');
    if(elHeader) elHeader.textContent = `${monthNames[month]} ${year}`;
    
    // Grid Generation
    const grid = document.getElementById('cal-grid');
    if(!grid) return;
    grid.innerHTML = '';
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Empty slots
    for(let i=0; i<firstDay; i++) {
        const div = document.createElement('div');
        div.className = 'cal-day empty';
        grid.appendChild(div);
    }
    
    const today = new Date();
    const selIso = formatDateISO(selectedDate);
    
    for(let d=1; d<=daysInMonth; d++) {
        const div = document.createElement('div');
        div.className = 'cal-day';
        div.textContent = d;
        
        // Check date string
        const currentIso = formatDateISO(new Date(year, month, d));
        
        // Highlight Today
        if (d === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
            div.classList.add('today');
        }
        
        // Highlight Selected
        if (currentIso === selIso) {
            div.classList.add('selected');
        }
        
        div.onclick = () => {
             selectedDate = new Date(year, month, d);
             refreshCalendar(); // Redraw selection
             loadDashboard(); // Fetch data for new date
        }
        
        grid.appendChild(div);
    }
}

function formatDateISO(dateObj) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

// Tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if(tabName === 'chat' || tabName === 'settings') {
        document.getElementById(`view-${tabName}`).classList.add('active');
        const tabs = document.querySelectorAll('.col-left .tab');
        if(tabName === 'chat') tabs[0].classList.add('active');
        if(tabName === 'settings') tabs[1].classList.add('active');
    }
}

// Chat
const chatInput = document.getElementById('chat-input');
if(chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    addMessage('You', text);
    chatInput.value = '';
    
    try {
        const response = await pywebview.api.process_command(text);
        addMessage('AI', response);
        
        if (response.includes("Scheduled") || response.includes("Added") || response.includes("deadline")) {
            loadDashboard();
        }
    } catch (err) {
        addMessage('AI', 'Error: ' + err);
    }
}

function addMessage(sender, text) {
    const history = document.getElementById('chat-history');
    if(!history) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender === 'You' ? 'user' : 'ai'}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    
    msgDiv.appendChild(bubble);
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
}

// Dashboard
async function loadDashboard() {
    try {
        const dateStr = formatDateISO(selectedDate);
        const data = await pywebview.api.get_dashboard_data(dateStr);
        
        // Update header
        const prettyDate = selectedDate.toDateString();
        const schedHeader = document.getElementById('schedule-header');
        if(schedHeader) schedHeader.textContent = `Schedule for ${prettyDate}`;

        // Split Tasks
        const dayTimed = data.tasks.filter(t => t.time);
        const dayUntimed = data.tasks.filter(t => !t.time && !t.completed);
        
        // Filter upcoming to remove duplicates if they are already in dayTimed
        const dayIds = new Set(data.tasks.map(t => t.id));
        const relevantUpcoming = data.upcoming.filter(u => !dayIds.has(u.id));
        
        const scheduleItems = [...dayTimed, ...relevantUpcoming];
        
        renderSchedule(scheduleItems);
        renderTodos(dayUntimed);
    } catch(err) {
        console.error("Dashboard Load Error", err);
    }
}

function renderSchedule(items) {
    const container = document.getElementById('deadlines-list');
    if(!container) return;
    container.innerHTML = '';
    
    if(!items.length) {
        container.innerHTML = '<div style="padding:10px; color:#666; font-size:12px">No upcoming events.</div>';
        return;
    }

    items.forEach(item => {
        const el = createTaskElement(item, true);
        container.appendChild(el);
    });
}

function renderTodos(items) {
    const container = document.getElementById('todo-list');
    if(!container) return;
    container.innerHTML = '';
    
    if(!items.length) {
        container.innerHTML = '<div style="padding:10px; color:#666; font-size:12px">No pending tasks.</div>';
        return;
    }

    items.forEach(item => {
        const el = createTaskElement(item, false);
        container.appendChild(el);
    });
}

function createTaskElement(item, showDate) {
    const div = document.createElement('div');
    div.className = 'task-item';
    
    const check = document.createElement('div');
    check.className = `task-check ${item.completed ? 'completed' : ''}`;
    check.onclick = async () => {
        await pywebview.api.toggle_task(item.id);
        loadDashboard();
    };
    
    const content = document.createElement('div');
    content.className = 'task-content';
    
    let titleHtml = `<div class="task-title">${item.title}</div>`;
    let metaHtml = '';
    
    if (item.category === 'Deadline') metaHtml += '<span style="color:#f9e2af"> Deadline </span>';
    if (showDate) metaHtml += `<span> ${item.date} </span>`;
    if (item.time) metaHtml += `<span> ${item.time}</span>`;
    
    content.innerHTML = titleHtml + `<div class="task-meta">${metaHtml}</div>`;
    
    const del = document.createElement('button');
    del.className = 'btn-del';
    del.innerHTML = '';
    del.onclick = async () => {
        await pywebview.api.delete_task(item.id);
        loadDashboard();
    };
    
    div.appendChild(check);
    div.appendChild(content);
    div.appendChild(del);
    return div;
}

async function addTask() {
    // For now simple prompt or we can inject a modal
    const text = prompt("Enter new task:");
    if(!text) return;
    
    await pywebview.api.quick_add_task(text);
    loadDashboard();
}

function updateSetting(key, val) {
    pywebview.api.update_setting(key, val);
}
