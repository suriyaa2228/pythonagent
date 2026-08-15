document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const pageTitle = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show target view
            const targetId = item.getAttribute('data-target');
            views.forEach(view => {
                view.style.display = view.id === targetId ? 'block' : 'none';
            });

            // Update title
            pageTitle.textContent = item.querySelector('span').textContent;

            // Load data if switching to reports
            if (targetId === 'reports-view') {
                loadReports();
            }
        });
    });

    // Test Runner Logic
    const testsTableBody = document.getElementById('tests-table-body');
    const selectAllCb = document.getElementById('select-all');
    const runSelectedBtn = document.getElementById('run-selected-btn');
    const runAllBtn = document.getElementById('run-all-btn');
    const refreshTestsBtn = document.getElementById('refresh-tests-btn');
    
    let activeTests = [];
    const executionMap = new Map();
    let pollingInterval = null;

    async function loadTests() {
        try {
            const res = await fetch('/api/v1/agent/tests');
            const data = await res.json();
            
            testsTableBody.innerHTML = '';
            
            if (data.tests.length === 0) {
                testsTableBody.innerHTML = '<tr><td colspan="4" class="empty-state">No tests found.</td></tr>';
                return;
            }

            data.tests.forEach(test => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><input type="checkbox" class="test-cb" value="${test.testId}"></td>
                    <td style="font-family: monospace;">${test.testId}</td>
                    <td>${test.name}</td>
                    <td>
                        <button class="icon-btn run-single-btn" data-id="${test.testId}" title="Run Test">
                            <i class="fa-solid fa-play" style="color: var(--success)"></i>
                        </button>
                    </td>
                `;
                testsTableBody.appendChild(tr);
            });

            attachTestListeners();
        } catch (e) {
            console.error("Failed to load tests", e);
        }
    }

    function attachTestListeners() {
        const checkboxes = document.querySelectorAll('.test-cb');
        
        selectAllCb.addEventListener('change', (e) => {
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            updateRunSelectedBtn();
        });

        checkboxes.forEach(cb => {
            cb.addEventListener('change', updateRunSelectedBtn);
        });

        document.querySelectorAll('.run-single-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const testId = e.currentTarget.getAttribute('data-id');
                runTestsBatch([testId]);
            });
        });
    }

    function updateRunSelectedBtn() {
        const anyChecked = document.querySelectorAll('.test-cb:checked').length > 0;
        runSelectedBtn.disabled = !anyChecked;
    }

    async function runTestsBatch(testIds) {
        if (!testIds || testIds.length === 0) return;
        
        try {
            const selectedEnv = document.getElementById('env-selector').value || 'stage';
            const res = await fetch('/api/v1/agent/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: "run_test", testIds: testIds, environment: selectedEnv })
            });
            const data = await res.json();
            
            const displayId = testIds.length === 1 ? testIds[0] : `BATCH_OF_${testIds.length}_TESTS`;
            addExecutionCard(data.executionId, displayId);
            
            // Start polling if not already
            if (!pollingInterval) {
                pollingInterval = setInterval(pollExecutions, 2000);
            }
        } catch (e) {
            console.error("Failed to run test batch", e);
            alert("Failed to trigger tests.");
        }
    }

    runSelectedBtn.addEventListener('click', () => {
        const selected = Array.from(document.querySelectorAll('.test-cb:checked')).map(cb => cb.value);
        if (selected.length > 0) {
            runTestsBatch(selected);
        }
    });

    runAllBtn.addEventListener('click', () => {
        const all = Array.from(document.querySelectorAll('.test-cb')).map(cb => cb.value);
        if (all.length > 0) {
            runTestsBatch(all);
        }
    });

    refreshTestsBtn.addEventListener('click', loadTests);

    // Executions Logic
    const executionsContainer = document.getElementById('executions-container');
    const modal = document.getElementById('execution-modal');
    const closeModalBtn = document.querySelector('.close-btn');
    let currentModalExecutionId = null;

    function addExecutionCard(execId, testId) {
        // Remove empty state if present
        const empty = executionsContainer.querySelector('.empty-state');
        if (empty) empty.remove();

        const div = document.createElement('div');
        div.className = 'execution-item';
        div.id = `exec-card-${execId}`;
        div.innerHTML = `
            <div class="exec-header">
                <strong>${testId}</strong>
                <span class="badge queued" id="badge-${execId}">QUEUED</span>
            </div>
            <div class="exec-id">${execId}</div>
            <div class="progress-container">
                <div class="progress-bar" id="prog-${execId}"></div>
            </div>
        `;
        
        div.addEventListener('click', () => openModal(execId, testId));
        executionsContainer.prepend(div);
        
        executionMap.set(execId, testId);

        if (!activeTests.includes(execId)) {
            activeTests.push(execId);
        }
    }

    async function pollExecutions() {
        if (activeTests.length === 0) {
            clearInterval(pollingInterval);
            pollingInterval = null;
            return;
        }

        for (let i = activeTests.length - 1; i >= 0; i--) {
            const execId = activeTests[i];
            try {
                const res = await fetch(`/api/v1/executions/${execId}`);
                if (!res.ok) continue;
                const data = await res.json();
                
                updateExecutionCard(execId, data.status);
                
                if (currentModalExecutionId === execId) {
                    updateModalContent(data);
                }

                if (['COMPLETED', 'FAILED'].includes(data.status)) {
                    activeTests.splice(i, 1);
                }
            } catch (e) {
                console.error("Poll failed for", execId);
            }
        }
    }

    function getStatusProgress(status) {
        switch(status) {
            case 'QUEUED': return '10%';
            case 'VALIDATING': return '30%';
            case 'EXECUTING': return '60%';
            case 'OBSERVING': return '90%';
            case 'COMPLETED': return '100%';
            case 'FAILED': return '100%';
            default: return '0%';
        }
    }

    function updateExecutionCard(execId, status) {
        const badge = document.getElementById(`badge-${execId}`);
        const prog = document.getElementById(`prog-${execId}`);
        if (!badge) return;
        
        badge.textContent = status;
        badge.className = 'badge';
        if (status === 'COMPLETED') badge.classList.add('success');
        else if (status === 'FAILED') badge.classList.add('error');
        else if (status === 'EXECUTING' || status === 'VALIDATING' || status === 'OBSERVING') badge.classList.add('running');
        else badge.classList.add('queued');

        if (prog) {
            prog.style.width = getStatusProgress(status);
            if (status === 'FAILED') {
                prog.style.background = 'var(--error)';
            } else if (status === 'COMPLETED') {
                prog.style.background = 'var(--success)';
            } else {
                prog.style.background = 'var(--primary)';
            }
        }

        const testId = executionMap.get(execId);
        if (testId && !testId.startsWith('BATCH_')) {
            const btn = document.querySelector(`.run-single-btn[data-id="${testId}"] i`);
            if (btn) {
                if (status === 'COMPLETED' || status === 'FAILED') {
                    btn.className = 'fa-solid fa-play';
                    btn.style.color = 'var(--success)';
                } else {
                    btn.className = 'fa-solid fa-pause';
                    btn.style.color = 'var(--secondary)';
                }
            }
        }
    }

    // Modal Logic
    function openModal(execId, testId) {
        currentModalExecutionId = execId;
        document.getElementById('modal-test-id').textContent = `${testId} (${execId})`;
        document.getElementById('modal-status').textContent = "LOADING...";
        document.getElementById('modal-logs').textContent = "Fetching logs...";
        modal.classList.add('show');
        
        // Fetch immediately once
        fetch(`/api/v1/executions/${execId}`)
            .then(r => r.json())
            .then(data => updateModalContent(data))
            .catch(e => console.error(e));
    }

    function updateModalContent(data) {
        const statusEl = document.getElementById('modal-status');
        const banner = document.getElementById('modal-status-banner');
        
        statusEl.textContent = data.status;
        banner.style.background = 'rgba(255,255,255,0.05)';
        if (data.status === 'COMPLETED') banner.style.background = 'rgba(16, 185, 129, 0.2)';
        if (data.status === 'FAILED') banner.style.background = 'rgba(239, 68, 68, 0.2)';

        const modalProg = document.getElementById('modal-progress-bar');
        if (modalProg) {
            modalProg.style.width = getStatusProgress(data.status);
            if (data.status === 'FAILED') {
                modalProg.style.background = 'var(--error)';
            } else if (data.status === 'COMPLETED') {
                modalProg.style.background = 'var(--success)';
            } else {
                modalProg.style.background = 'var(--primary)';
            }
        }

        let logs = "";
        if (data.stdout) logs += data.stdout + "\n";
        if (data.stderr) logs += "[ERROR] " + data.stderr + "\n";
        if (data.failure_message) logs += "\n[FAILURE] " + data.failure_message;
        
        document.getElementById('modal-logs').textContent = logs || "No logs available yet.";
    }

    closeModalBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        currentModalExecutionId = null;
    });

    // Reports Logic
    const reportsGrid = document.getElementById('reports-grid-container');
    const refreshReportsBtn = document.getElementById('refresh-reports-btn');

    async function loadReports() {
        try {
            const res = await fetch('/api/v1/reports');
            const files = await res.json();
            
            reportsGrid.innerHTML = '';
            
            if (files.length === 0) {
                reportsGrid.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;">No reports generated yet.</div>';
                return;
            }

            files.forEach(file => {
                const a = document.createElement('a');
                a.href = `/api/v1/reports/${file}`;
                a.target = "_blank";
                a.className = "report-card";
                a.style.position = "relative";
                
                a.innerHTML = `
                    <i class="fa-solid fa-file-code"></i>
                    <div class="report-name">${file}</div>
                    <button class="delete-report-btn" data-file="${file}" title="Delete Report" style="position: absolute; top: 10px; right: 10px; background: rgba(239, 68, 68, 0.1); border: none; color: #ef4444; border-radius: 4px; padding: 6px 8px; cursor: pointer;">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                reportsGrid.appendChild(a);
            });

            // Attach delete listeners
            document.querySelectorAll('.delete-report-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    e.preventDefault(); // Prevent navigating to the report link
                    e.stopPropagation();
                    const file = e.currentTarget.getAttribute('data-file');
                    if (confirm(`Are you sure you want to delete ${file}?`)) {
                        try {
                            const response = await fetch(`/api/v1/reports/${file}`, { method: 'DELETE' });
                            if (response.ok) {
                                loadReports();
                            } else {
                                alert("Failed to delete report.");
                            }
                        } catch (err) {
                            console.error("Delete failed", err);
                        }
                    }
                });
            });
        } catch (e) {
            console.error("Failed to load reports", e);
        }
    }

    refreshReportsBtn.addEventListener('click', loadReports);

    // Initial load
    loadTests();
});
