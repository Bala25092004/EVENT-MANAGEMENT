document.addEventListener('DOMContentLoaded', function () {
    const html = document.documentElement;

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            html.classList.toggle('dark');
            localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
        });
    }
    if (localStorage.getItem('theme') === 'dark') {
        html.classList.add('dark');
    }

    // --- Add Event Modal ---
    const addEventModal = document.getElementById('add-event-modal');
    const addEventBtn = document.getElementById('add-event-btn');
    if (addEventBtn) addEventBtn.addEventListener('click', () => addEventModal.classList.remove('hidden'));
    document.getElementById('cancel-event-btn')?.addEventListener('click', () => addEventModal.classList.add('hidden'));
    document.getElementById('add-event-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const eventData = { title: document.getElementById('title').value, description: document.getElementById('description').value, date: document.getElementById('date').value, location: document.getElementById('location').value, capacity: document.getElementById('capacity').value, image_url: document.getElementById('image_url').value };
        const response = await fetch('/event/new', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(eventData) });
        const result = await response.json();
        if (result.success) {
            addEventModal.classList.add('hidden');
            showQrCodeModal(result.event_url, result.qr_code, result.event_title, true);
        } else { alert(`Error: ${result.message}`); }
    });

    // --- Edit Event Modal ---
    const editEventModal = document.getElementById('edit-event-modal');
    document.querySelectorAll('.edit-event-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const eventId = e.target.dataset.eventId;
            const response = await fetch(`/api/event/${eventId}`);
            const data = await response.json();
            document.getElementById('edit-event-id').value = data.id;
            document.getElementById('edit-title').value = data.title;
            document.getElementById('edit-description').value = data.description;
            document.getElementById('edit-date').value = data.date;
            document.getElementById('edit-location').value = data.location;
            document.getElementById('edit-capacity').value = data.capacity;
            document.getElementById('edit-image_url').value = data.image_url;
            editEventModal.classList.remove('hidden');
        });
    });
    document.getElementById('cancel-edit-btn')?.addEventListener('click', () => editEventModal.classList.add('hidden'));
    document.getElementById('edit-event-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const eventId = document.getElementById('edit-event-id').value;
        const updatedData = { title: document.getElementById('edit-title').value, description: document.getElementById('edit-description').value, date: document.getElementById('edit-date').value, location: document.getElementById('edit-location').value, capacity: document.getElementById('edit-capacity').value, image_url: document.getElementById('edit-image_url').value };
        const response = await fetch(`/event/update/${eventId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updatedData) });
        const result = await response.json();
        if (result.success) {
            editEventModal.classList.add('hidden');
            window.location.reload();
        } else { alert(`Error: ${result.message}`); }
    });

    // --- Share Event Button Logic ---
    document.querySelectorAll('.share-event-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const eventId = e.target.dataset.eventId;
            const response = await fetch(`/api/event/share/${eventId}`);
            const result = await response.json();
            if (result.success) {
                showQrCodeModal(result.event_url, result.qr_code, result.event_title, false);
            }
        });
    });

    // --- QR Code / Share Modal Logic ---
    const qrCodeModal = document.getElementById('qr-code-modal');
    let reloadAfterClose = false;
    function showQrCodeModal(eventUrl, qrCodeData, eventTitle, shouldReload) {
        if (qrCodeModal) {
            document.getElementById('qr-code-img').src = qrCodeData;
            document.getElementById('event-url-input').value = eventUrl;
            document.getElementById('qr-modal-title').textContent = `Share "${eventTitle}"`;
            qrCodeModal.classList.remove('hidden');
            reloadAfterClose = shouldReload;
            const webShareBtn = document.getElementById('web-share-btn');
            if (webShareBtn) {
                webShareBtn.dataset.url = eventUrl;
                webShareBtn.dataset.title = eventTitle;
            }
        }
    }
    document.getElementById('close-qr-modal-btn')?.addEventListener('click', () => {
        if (qrCodeModal) {
            qrCodeModal.classList.add('hidden');
        }
        if (reloadAfterClose) {
            window.location.reload();
        }
    });
    const copyUrlBtn = document.getElementById('copy-url-btn');
    if (copyUrlBtn) {
        copyUrlBtn.addEventListener('click', () => {
            const urlInput = document.getElementById('event-url-input');
            urlInput.select();
            document.execCommand('copy');
            copyUrlBtn.textContent = 'Copied!';
            setTimeout(() => copyUrlBtn.textContent = 'Copy Link', 2000);
        });
    }
    const webShareBtn = document.getElementById('web-share-btn');
    if (webShareBtn) {
        webShareBtn.addEventListener('click', async () => {
            const shareData = { title: webShareBtn.dataset.title, url: webShareBtn.dataset.url };
            if (navigator.share) {
                try { await navigator.share(shareData); } catch (err) { console.error('Share failed:', err); }
            } else {
                alert('Web Share not supported. Please copy the link manually.');
                copyUrlBtn.click();
            }
        });
    }

    // --- Reports Page Logic ---
    const revenueChartCanvas = document.getElementById('revenueChart');
    if (revenueChartCanvas) {
        fetch('/api/reports-data')
            .then(response => response.json())
            .then(data => {
                // 1. Populate Stat Cards
                document.getElementById('total-revenue').textContent = `$${data.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                document.getElementById('total-revenue-attendees').textContent = `from ${data.total_attendees} attendees`;
                document.getElementById('avg-ticket-price').textContent = `$${data.avg_ticket_price.toFixed(2)}`;
                document.getElementById('total-events').textContent = data.total_events;
                document.getElementById('total-events-attendees').textContent = `with ${data.total_attendees} attendees`;

                // 2. Render Revenue Bar Chart
                new Chart(revenueChartCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.revenue_by_event.labels,
                        datasets: [{ label: 'Revenue', data: data.revenue_by_event.data, backgroundColor: '#3B82F6' }]
                    },
                    options: { scales: { y: { beginAtZero: true } } }
                });

                // 3. Render Event Status Doughnut Chart
                const statusChartCanvas = document.getElementById('statusChart');
                new Chart(statusChartCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: ['Upcoming', 'Past'],
                        datasets: [{ data: [data.event_status.upcoming, data.event_status.past], backgroundColor: ['#3B82F6', '#9CA3AF'], hoverOffset: 4 }]
                    }
                });

                // 4. Populate Top Events Table
                const topEventsBody = document.getElementById('top-events-body');
                topEventsBody.innerHTML = '';
                data.top_events.slice(0, 5).forEach(event => {
                    const row = `
                        <tr class="border-b dark:border-gray-700">
                            <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">${event.title}</td>
                            <td class="px-4 py-3">${event.tickets}</td>
                            <td class="px-4 py-3">$${event.price.toFixed(2)}</td>
                            <td class="px-4 py-3 font-bold">$${event.revenue.toLocaleString()}</td>
                        </tr>`;
                    topEventsBody.innerHTML += row;
                });

                // 5. Populate Event Performance Table
                const performanceBody = document.getElementById('performance-body');
                performanceBody.innerHTML = '';
                data.event_performance.slice(0, 5).forEach(event => {
                    const row = `
                        <tr class="border-b dark:border-gray-700">
                            <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">${event.title}</td>
                            <td class="px-4 py-3">${event.sold}/${event.capacity}</td>
                            <td class="px-4 py-3">
                                <div class="flex items-center gap-2">
                                    <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${event.occupancy.toFixed(0)}%"></div>
                                    </div>
                                    <span>${event.occupancy.toFixed(0)}%</span>
                                </div>
                            </td>
                        </tr>`;
                    performanceBody.innerHTML += row;
                });
            });
    }

    // --- Event Search Logic ---
    const eventSearchInput = document.getElementById('event-search-input');
    if (eventSearchInput) {
        const eventGrid = document.getElementById('event-grid');
        const allEventCards = eventGrid.querySelectorAll('.event-card');
        const noEventResults = document.getElementById('no-event-results');

        eventSearchInput.addEventListener('keyup', () => {
            const searchTerm = eventSearchInput.value.toLowerCase();
            let visibleCount = 0;

            allEventCards.forEach(card => {
                const cardText = card.textContent.toLowerCase();
                if (cardText.includes(searchTerm)) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            noEventResults.classList.toggle('hidden', visibleCount > 0);
        });
    }

    // --- Attendee Search Logic ---
    const attendeeSearchInput = document.getElementById('attendee-search-input');
    if (attendeeSearchInput) {
        const attendeeTableBody = document.getElementById('attendee-table-body');
        const allRows = Array.from(attendeeTableBody.querySelectorAll('tr'));
        const noResultsRow = allRows.find(row => row.id === 'no-results-row');

        attendeeSearchInput.addEventListener('keyup', () => {
            const searchTerm = attendeeSearchInput.value.toLowerCase();
            let visibleRows = 0;

            allRows.filter(row => row.id !== 'no-results-row' && row.id !== 'no-attendees-row').forEach(row => {
                const rowText = row.textContent.toLowerCase();
                if (rowText.includes(searchTerm)) {
                    row.style.display = '';
                    visibleRows++;
                } else {
                    row.style.display = 'none';
                }
            });

            if (noResultsRow) {
                noResultsRow.classList.toggle('hidden', visibleRows > 0 || allRows.length <= 1);
            }
        });
    }
});