let routinesData = [];
let currentView = 'batch'; // 'batch' or 'slots'

async function init() {
    try {
        const response = await fetch('routines.json');
        const data = await response.json();
        routinesData = data.batches;
        
        populateRoomDropdown();
        attachEventListeners();
        updateDashboard();
    } catch (error) {
        console.error('Error loading routines:', error);
        document.getElementById('dashboard').innerHTML = '<div class="no-results">Error loading data. Please make sure routines.json exists.</div>';
    }
}

function populateRoomDropdown() {
    const rooms = new Set();
    routinesData.forEach(batch => {
        if (batch.room && batch.room !== 'Unknown') rooms.add(batch.room);
        if (batch.schedule) {
            batch.schedule.forEach(s => {
                if (s.room && s.room !== 'Unknown') rooms.add(s.room);
            });
        }
    });

    const roomSelect = document.getElementById('room-filter');
    const sortedRooms = Array.from(rooms).sort();
    sortedRooms.forEach(room => {
        const opt = document.createElement('option');
        opt.value = room;
        opt.textContent = room;
        roomSelect.appendChild(opt);
    });
}

function attachEventListeners() {
    const searchInput = document.getElementById('search-input');
    const dayFilter = document.getElementById('day-filter');
    const roomFilter = document.getElementById('room-filter');
    const btnBatch = document.getElementById('view-batch');
    const btnSlots = document.getElementById('view-slots');

    const handleUpdate = () => updateDashboard();

    searchInput.addEventListener('input', handleUpdate);
    dayFilter.addEventListener('change', handleUpdate);
    roomFilter.addEventListener('change', handleUpdate);

    btnBatch.addEventListener('click', () => {
        currentView = 'batch';
        btnBatch.classList.add('active');
        btnSlots.classList.remove('active');
        updateDashboard();
    });

    btnSlots.addEventListener('click', () => {
        currentView = 'slots';
        btnSlots.classList.add('active');
        btnBatch.classList.remove('active');
        updateDashboard();
    });
}

function updateDashboard() {
    const term = document.getElementById('search-input').value.toLowerCase().trim();
    const day = document.getElementById('day-filter').value;
    const room = document.getElementById('room-filter').value;

    if (currentView === 'batch') {
        const filteredBatches = routinesData.filter(batch => {
            // Check basic info
            const basicMatch = !term || 
                (batch.name || "").toLowerCase().includes(term) || 
                (batch.semester || "").toLowerCase().includes(term) || 
                (batch.counsellor || "").toLowerCase().includes(term);

            // Check courses (for term)
            const courseMatch = !term || (batch.courses && batch.courses.some(c => 
                (c.name || "").toLowerCase().includes(term) || 
                (c.code || "").toLowerCase().includes(term) || 
                (c.teacher || "").toLowerCase().includes(term)
            ));

            // Check schedule (for Day, Room, and Term)
            const scheduleMatch = (batch.schedule || []).some(s => {
                const dMatch = !day || s.day === day;
                const rMatch = !room || s.room === room || batch.room === room;
                const tMatch = !term || (s.course_code || "").toLowerCase().includes(term) || (s.time || "").toLowerCase().includes(term);
                return dMatch && rMatch && tMatch;
            });

            // If we have filters active (day/room), we MUST have a schedule match
            if (day || room) return scheduleMatch;
            
            return basicMatch || courseMatch || scheduleMatch;
        });
        renderBatchView(filteredBatches);
    } else {
        // Finder View: Flat list of all sessions across all batches
        const allSlots = [];
        routinesData.forEach(batch => {
            if (batch.schedule) {
                batch.schedule.forEach(slot => {
                    const dMatch = !day || slot.day === day;
                    const rMatch = !room || slot.room === room;
                    
                    // For Finder View, if term is set, it can match anything in the slot or batch info
                    const course = batch.courses ? batch.courses.find(c => c.code === slot.course_code) : null;
                    const textMatch = !term || 
                        (slot.course_code || "").toLowerCase().includes(term) ||
                        (slot.day || "").toLowerCase().includes(term) ||
                        (slot.time || "").toLowerCase().includes(term) ||
                        (slot.room || "").toLowerCase().includes(term) ||
                        (batch.name || "").toLowerCase().includes(term) ||
                        (course && (course.name.toLowerCase().includes(term) || course.teacher.toLowerCase().includes(term)));

                    if (dMatch && rMatch && textMatch) {
                        allSlots.push({ ...slot, batchName: batch.name, course: course });
                    }
                });
            }
        });
        renderMasterView(allSlots);
    }
}

function renderBatchView(batches) {
    const container = document.getElementById('dashboard');
    const term = document.getElementById('search-input').value.toLowerCase().trim();
    const day = document.getElementById('day-filter').value;
    const room = document.getElementById('room-filter').value;

    if (batches.length === 0) {
        container.innerHTML = '<div class="no-results"><i class="fas fa-search"></i> No routines found matching your search.</div>';
        return;
    }

    container.innerHTML = batches.map(batch => {
        // Filter schedule items within the batch if filters are active
        const displaySchedule = (batch.schedule || []).filter(s => {
            const dMatch = !day || s.day === day;
            const rMatch = !room || s.room === room;
            const course = batch.courses ? batch.courses.find(c => c.code === s.course_code) : null;
            const textMatch = !term || 
                s.course_code.toLowerCase().includes(term) ||
                (course && (course.name.toLowerCase().includes(term) || course.teacher.toLowerCase().includes(term)));
            return dMatch && rMatch && textMatch;
        });

        if (displaySchedule.length === 0) return '';

        return `
            <div class="batch-card">
                <div class="batch-name">${batch.name}</div>
                <div class="batch-info">
                    <strong>Counsellor:</strong> ${batch.counsellor || 'N/A'}
                </div>
                <div class="schedule-grid">
                    ${displaySchedule.map(s => {
                        const course = batch.courses ? batch.courses.find(c => c.code === s.course_code) : null;
                        return `
                            <div class="schedule-item">
                                <div class="day-label">${s.day} <small>(${s.time})</small></div>
                                <div class="course-code">${s.course_code}</div>
                                <div class="course-name">${course ? course.name : 'N/A'}</div>
                                <div class="teacher-name">${course ? course.teacher : ''}</div>
                                <div class="room-tag">
                                    <i class="fas fa-map-marker-alt"></i> ${s.room}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function renderMasterView(slots) {
    const container = document.getElementById('dashboard');
    if (slots.length === 0) {
        container.innerHTML = '<div class="no-results"><i class="fas fa-search"></i> No individual classes found matching these filters.</div>';
        return;
    }

    const dayOrder = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    slots.sort((a,b) => dayOrder.indexOf(a.day) - dayOrder.indexOf(b.day) || a.time.localeCompare(b.time));

    container.innerHTML = slots.map(slot => `
        <div class="master-slot-item">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div class="master-slot-time">${slot.day}, ${slot.time}</div>
                    <div class="course-name" style="font-size: 1.1rem; margin: 4px 0;">${slot.course ? slot.course.name : slot.course_code}</div>
                    <div class="room-tag">
                        <span><i class="fas fa-users"></i> Batch: ${slot.batchName}</span> | 
                        <span><i class="fas fa-map-marker-alt"></i> <strong>${slot.room}</strong></span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="course-code" style="color: var(--primary-light)">${slot.course_code}</div>
                    <div class="teacher-name">${slot.course ? slot.course.teacher : ''}</div>
                </div>
            </div>
        </div>
    `).join('');
}

document.addEventListener('DOMContentLoaded', init);
