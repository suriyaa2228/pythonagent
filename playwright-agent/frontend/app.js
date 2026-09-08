// AI Playwright Automation Studio Frontend Controller

document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');

    const subtitles = {
        'generator-view': 'Convert user stories into framework-compliant Python Playwright tests',
        'workspace-view': 'Inspect, edit, validate, and conversationally modify generated tests',
        'runner-view': 'Execute tests in isolated workspaces with real-time logs',
        'reports-view': 'Comprehensive Extent Report execution telemetry and metrics'
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            views.forEach(v => v.style.display = 'none');

            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            const targetView = document.getElementById(targetId);
            if (targetView) {
                targetView.style.display = 'block';
                pageTitle.textContent = item.querySelector('span').textContent;
                pageSubtitle.textContent = subtitles[targetId] || '';

                if (targetId === 'runner-view') loadAvailableTests();
                if (targetId === 'reports-view') loadReportsSummary();
            }
        });
    });

    // Elements
    const generateBtn = document.getElementById('generate-btn');
    const userStoryInput = document.getElementById('user-story-input');
    const acInput = document.getElementById('ac-input');
    const envSelect = document.getElementById('env-select');
    const scriptCodeEditor = document.getElementById('script-code-editor');
    const validationBadge = document.getElementById('validation-badge');
    const validationSummary = document.getElementById('validation-summary');
    const validateBtn = document.getElementById('validate-btn');
    const runScriptBtn = document.getElementById('run-script-btn');
    const copyScriptBtn = document.getElementById('copy-script-btn');

    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');

    // Runner Elements
    const selectAllCheckbox = document.getElementById('select-all-tests');
    const runSelectedBtn = document.getElementById('run-selected-tests-btn');
    const refreshTestsBtn = document.getElementById('refresh-tests-btn');
    const runnerEnvSelect = document.getElementById('runner-env-select');
    const refreshReportsBtn = document.getElementById('refresh-reports-btn');

    // 1. Generate Test Action
    generateBtn.addEventListener('click', async () => {
        const userStory = userStoryInput.value.trim();
        const rawAc = acInput.value.trim();
        const acceptanceCriteria = rawAc.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        const environment = envSelect.value;

        if (!userStory) {
            alert('Please enter a user story.');
            return;
        }

        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating with LangChain & Groq...';

        try {
            const res = await fetch('/api/v1/ai/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userStory,
                    acceptanceCriteria,
                    project: 'playwright',
                    environment
                })
            });

            const data = await res.json();
            if (data.pythonScript) {
                scriptCodeEditor.value = data.pythonScript;
                updateValidationUI(data.validation);

                // Switch to workspace view
                const workspaceNav = document.querySelector('[data-target="workspace-view"]');
                if (workspaceNav) workspaceNav.click();

                appendChatMessage('assistant', `Test **${data.testName || 'GeneratedTest'}** generated successfully with ${data.ragContextCount || 0} framework context artifacts.`);
            } else {
                alert('Generation error: ' + JSON.stringify(data));
            }
        } catch (err) {
            alert('Request failed: ' + err.message);
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fa-solid fa-sparkles"></i> Generate Python Playwright Script';
        }
    });

    // 2. Validate Script Action
    validateBtn.addEventListener('click', async () => {
        const code = scriptCodeEditor.value.trim();
        if (!code) return;

        validateBtn.disabled = true;
        try {
            const res = await fetch('/api/v1/ai/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pythonScript: code })
            });
            const data = await res.json();
            updateValidationUI(data);
        } catch (err) {
            alert('Validation failed: ' + err.message);
        } finally {
            validateBtn.disabled = false;
        }
    });

    // 3. Execute Script from Workspace Action
    runScriptBtn.addEventListener('click', async () => {
        const code = scriptCodeEditor.value.trim();
        if (!code) {
            alert('No script in workspace to execute.');
            return;
        }

        runScriptBtn.disabled = true;
        runScriptBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running...';

        // Switch to runner view
        const runnerNav = document.querySelector('[data-target="runner-view"]');
        if (runnerNav) runnerNav.click();

        const consoleBox = document.getElementById('execution-logs');
        consoleBox.innerHTML = '<div class="console-line text-primary"><i class="fa-solid fa-gear fa-spin"></i> Spawning isolated pytest execution workspace...</div>';

        try {
            const res = await fetch('/api/v1/ai/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pythonScript: code,
                    testName: 'test_generated_tc.py',
                    environment: envSelect.value,
                    headless: true
                })
            });

            const data = await res.json();
            const colorClass = data.status === 'PASSED' ? 'text-success' : 'text-danger';
            consoleBox.innerHTML = `
                <div class="console-line ${colorClass}">[EXECUTION ${data.status}] ID: ${data.executionId} (Duration: ${data.durationSeconds}s)</div>
                <div class="console-line mt-4">--- STDOUT ---</div>
                <pre class="console-line text-muted">${escapeHtml(data.stdout || '')}</pre>
                ${data.stderr ? `<div class="console-line text-danger mt-4">--- STDERR ---</div><pre class="console-line text-danger">${escapeHtml(data.stderr)}</pre>` : ''}
            `;
        } catch (err) {
            consoleBox.innerHTML += `<div class="console-line text-danger">Execution error: ${err.message}</div>`;
        } finally {
            runScriptBtn.disabled = false;
            runScriptBtn.innerHTML = '<i class="fa-solid fa-play"></i> Execute';
        }
    });

    // 4. AI Chat Modification
    async function sendChat() {
        const message = chatInput.value.trim();
        const currentScript = scriptCodeEditor.value.trim();
        if (!message || !currentScript) return;

        appendChatMessage('user', message);
        chatInput.value = '';
        sendChatBtn.disabled = true;

        const loadingMsg = appendChatMessage('assistant', '<i class="fa-solid fa-spinner fa-spin"></i> Applying modifications to script...');

        try {
            const res = await fetch('/api/v1/ai/modify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    currentScript,
                    message
                })
            });

            const data = await res.json();
            if (data.pythonScript) {
                scriptCodeEditor.value = data.pythonScript;
                updateValidationUI(data.validation);
                loadingMsg.innerHTML = `<i class="fa-solid fa-check text-success"></i> ${data.description || 'Script updated successfully.'}`;
            } else {
                loadingMsg.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-danger"></i> Could not modify script: ${JSON.stringify(data)}`;
            }
        } catch (err) {
            loadingMsg.innerHTML = `<i class="fa-solid fa-circle-xmark text-danger"></i> Chat request failed: ${err.message}`;
        } finally {
            sendChatBtn.disabled = false;
        }
    }

    sendChatBtn.addEventListener('click', sendChat);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChat();
    });

    // 5. Copy Script Action
    copyScriptBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(scriptCodeEditor.value);
        copyScriptBtn.innerHTML = '<i class="fa-solid fa-check text-success"></i>';
        setTimeout(() => copyScriptBtn.innerHTML = '<i class="fa-solid fa-copy"></i>', 2000);
    });

    // 6. Reports Summary Loader
    const deleteAllReportsBtn = document.getElementById('delete-all-reports-btn');

    async function loadReportsSummary() {
        const tbody = document.getElementById('reports-table-body');
        tbody.innerHTML = '<tr><td colspan="7" class="text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Loading Extent Reports...</td></tr>';

        try {
            const res = await fetch('/api/v1/ai/reports/summary');
            const data = await res.json();

            document.getElementById('metric-total-reports').textContent = data.totalReports || 0;
            const passMetric = document.getElementById('metric-passed');
            if (passMetric) {
                passMetric.textContent = (data.averagePassRate !== undefined ? data.averagePassRate : 100) + '%';
            }

            if (!data.reports || data.reports.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-muted">No Extent Reports found in python_playwright/reports.</td></tr>';
                return;
            }

            let html = '';
            data.reports.forEach(r => {
                const statusBadge = r.overallStatus === 'PASSED' 
                    ? '<span class="badge badge-pass">PASS</span>'
                    : '<span class="badge badge-fail">FAIL</span>';

                html += `
                    <tr>
                        <td><strong>${escapeHtml(r.fileName)}</strong></td>
                        <td>${r.totalTestCases || 1}</td>
                        <td class="text-success">${r.passed || 0}</td>
                        <td class="text-danger">${r.failed || 0}</td>
                        <td>${r.passPercentage !== undefined ? r.passPercentage : 100}%</td>
                        <td>${statusBadge}</td>
                        <td>
                            <a href="/api/v1/reports/${encodeURIComponent(r.fileName)}" target="_blank" class="btn outline-btn btn-sm style-inline-action">
                                <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Extent HTML
                            </a>
                            <button class="btn danger-btn btn-sm delete-single-report-btn" data-filename="${escapeHtml(r.fileName)}">
                                <i class="fa-solid fa-trash"></i> Delete
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;

            // Wire individual delete buttons
            document.querySelectorAll('.delete-single-report-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const fileName = btn.getAttribute('data-filename');
                    if (confirm(`Are you sure you want to delete report '${fileName}'?`)) {
                        try {
                            const delRes = await fetch(`/api/v1/reports/${encodeURIComponent(fileName)}`, { method: 'DELETE' });
                            const delData = await delRes.json();
                            if (delRes.ok && (delData.status === 'success' || !delData.error)) {
                                loadReportsSummary();
                            } else {
                                alert('Failed to delete report: ' + (delData.error || delData.message || 'Unknown error'));
                            }
                        } catch (err) {
                            alert('Delete request error: ' + err.message);
                        }
                    }
                });
            });

        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-danger">Failed to load reports: ${err.message}</td></tr>`;
        }
    }

    if (refreshReportsBtn) {
        refreshReportsBtn.addEventListener('click', loadReportsSummary);
    }

    if (deleteAllReportsBtn) {
        deleteAllReportsBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete ALL Extent Reports?')) {
                try {
                    const res = await fetch('/api/v1/reports', { method: 'DELETE' });
                    const data = await res.json();
                    if (res.ok) {
                        loadReportsSummary();
                    } else {
                        alert('Failed to delete all reports: ' + (data.error || 'Unknown error'));
                    }
                } catch (err) {
                    alert('Delete all reports error: ' + err.message);
                }
            }
        });
    }


    // 7. Test Suite Loader & Runner
    async function loadAvailableTests() {
        const tbody = document.getElementById('tests-table-body');
        tbody.innerHTML = '<tr><td colspan="4" class="text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Loading test catalog...</td></tr>';

        try {
            const res = await fetch('/api/v1/agent/tests');
            const data = await res.json();

            if (!data.tests || data.tests.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-muted">No existing test files found.</td></tr>';
                return;
            }

            let html = '';
            data.tests.forEach(t => {
                html += `
                    <tr>
                        <td><input type="checkbox" class="test-checkbox" value="${escapeHtml(t.testId)}"></td>
                        <td><code>${escapeHtml(t.testId)}</code></td>
                        <td>${escapeHtml(t.name)}</td>
                        <td>
                            <button class="btn outline-btn btn-sm run-single-btn" data-id="${escapeHtml(t.testId)}">
                                <i class="fa-solid fa-play"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;

            // Wire up single run buttons
            document.querySelectorAll('.run-single-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const testId = btn.getAttribute('data-id');
                    executeTestBatch([testId]);
                });
            });

            // Wire up checkboxes
            document.querySelectorAll('.test-checkbox').forEach(cb => {
                cb.addEventListener('change', updateRunSelectedState);
            });

        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-danger">Failed to load tests: ${err.message}</td></tr>`;
        }
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', () => {
            document.querySelectorAll('.test-checkbox').forEach(cb => {
                cb.checked = selectAllCheckbox.checked;
            });
            updateRunSelectedState();
        });
    }

    function updateRunSelectedState() {
        const checked = document.querySelectorAll('.test-checkbox:checked');
        if (runSelectedBtn) {
            runSelectedBtn.disabled = checked.length === 0;
            runSelectedBtn.textContent = checked.length > 0 ? `Run Selected (${checked.length})` : 'Run Selected';
        }
    }

    if (runSelectedBtn) {
        runSelectedBtn.addEventListener('click', () => {
            const checked = Array.from(document.querySelectorAll('.test-checkbox:checked')).map(cb => cb.value);
            if (checked.length > 0) {
                executeTestBatch(checked);
            }
        });
    }

    if (refreshTestsBtn) {
        refreshTestsBtn.addEventListener('click', loadAvailableTests);
    }

    // Save Modal Elements
    const saveScriptBtn = document.getElementById('save-script-btn');
    const saveTestModal = document.getElementById('save-test-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalSubmitBtn = document.getElementById('modal-submit-btn');
    const modalTcNumber = document.getElementById('modal-tc-number');
    const modalTcName = document.getElementById('modal-tc-name');
    const modalErrorBox = document.getElementById('modal-error-box');

    const runnerEngineSelect = document.getElementById('runner-engine-select');

    // Modal Trigger Logic
    if (saveScriptBtn && saveTestModal) {
        saveScriptBtn.addEventListener('click', () => {
            const script = scriptCodeEditor.value.trim();
            if (!script) {
                alert('No generated script in workspace to save.');
                return;
            }
            modalErrorBox.style.display = 'none';
            modalErrorBox.textContent = '';
            saveTestModal.style.display = 'flex';
        });
    }

    function closeModal() {
        if (saveTestModal) saveTestModal.style.display = 'none';
    }

    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
    if (modalCancelBtn) modalCancelBtn.addEventListener('click', closeModal);

    if (modalSubmitBtn) {
        modalSubmitBtn.addEventListener('click', async () => {
            const tcNumber = modalTcNumber.value.trim();
            const tcName = modalTcName.value.trim();
            const pythonScript = scriptCodeEditor.value.trim();

            if (!tcNumber || !tcName) {
                modalErrorBox.style.display = 'block';
                modalErrorBox.textContent = 'Both Test Case Number and Test Case Name are mandatory.';
                return;
            }

            modalSubmitBtn.disabled = true;
            modalSubmitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

            try {
                const res = await fetch('/api/v1/ai/save-test-case', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        testCaseNumber: tcNumber,
                        testCaseName: tcName,
                        pythonScript: pythonScript,
                        environment: envSelect ? envSelect.value : 'stage'
                    })
                });

                const data = await res.json();
                if (res.ok && data.success) {
                    closeModal();
                    modalTcNumber.value = '';
                    modalTcName.value = '';
                    appendChatMessage('assistant', `<i class="fa-solid fa-circle-check text-success"></i> Test Case <strong>${escapeHtml(tcNumber)} - ${escapeHtml(tcName)}</strong> persisted successfully!`);
                    
                    // Switch to runner view and reload test list catalog
                    const runnerNav = document.querySelector('[data-target="runner-view"]');
                    if (runnerNav) runnerNav.click();
                } else {
                    modalErrorBox.style.display = 'block';
                    modalErrorBox.textContent = data.detail || data.message || 'Failed to save test case.';
                }
            } catch (err) {
                modalErrorBox.style.display = 'block';
                modalErrorBox.textContent = 'Save request failed: ' + err.message;
            } finally {
                modalSubmitBtn.disabled = false;
                modalSubmitBtn.innerHTML = '<i class="fa-solid fa-check"></i> Save Test Case';
            }
        });
    }

    const runnerModeSelect = document.getElementById('runner-mode-select');

    // Helper to reset and show runner progress bar
    function showRunnerProgress(totalTests, firstTestName) {
        const container = document.getElementById('progress-container');
        const fill = document.getElementById('progress-bar-fill');
        const statusText = document.getElementById('progress-status-text');
        const percentText = document.getElementById('progress-percent-text');
        const currentTestName = document.getElementById('current-test-name');
        const badge = document.getElementById('runner-status-badge');

        if (container) container.style.display = 'flex';
        if (fill) {
            fill.style.width = '0%';
            fill.style.background = 'linear-gradient(90deg, #4f46e5, #818cf8, #10b981)';
        }
        if (statusText) statusText.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-primary"></i> Executing Suite (0/${totalTests} Completed)`;
        if (percentText) percentText.textContent = '0%';
        if (currentTestName) currentTestName.textContent = `Running Test 1 of ${totalTests}: ${firstTestName || 'Initializing...'}`;
        if (badge) {
            badge.className = 'badge badge-executing';
            badge.textContent = 'RUNNING';
        }
    }

    // Execute Test Batch Function (Supports Pytest Subprocess vs Playwright MCP Agent)
    async function executeTestBatch(testIds) {
        const env = runnerEnvSelect ? runnerEnvSelect.value : 'stage';
        const engine = runnerEngineSelect ? runnerEngineSelect.value : 'PYTEST';
        const isHeadless = runnerModeSelect ? (runnerModeSelect.value === 'true') : false;
        const consoleBox = document.getElementById('execution-logs');

        showRunnerProgress(testIds.length, testIds[0]);

        consoleBox.innerHTML = `<div class="console-line text-primary"><i class="fa-solid fa-spinner fa-spin"></i> Launching test suite run (${engine === 'MCP_AGENT' ? 'Playwright MCP Agent' : 'Pytest Engine'}) for [${testIds.join(', ')}] on environment '${env}' (${isHeadless ? 'Headless' : 'Headed'})...</div>`;

        try {
            const res = await fetch('/api/v1/agent/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'run_test',
                    testIds: testIds,
                    environment: env,
                    engine: engine,
                    headless: isHeadless
                })
            });

            const data = await res.json();
            if (data.executionId) {
                consoleBox.innerHTML += `<div class="console-line text-success">Task created: ${data.taskId} | Execution ID: ${data.executionId}</div>`;
                pollExecutionProgress(data.executionId);
            } else {
                consoleBox.innerHTML += `<div class="console-line text-danger">Failed to start execution: ${JSON.stringify(data)}</div>`;
            }
        } catch (err) {
            consoleBox.innerHTML += `<div class="console-line text-danger">Error: ${err.message}</div>`;
        }
    }

    // Poll execution status
    async function pollExecutionProgress(executionId) {
        const consoleBox = document.getElementById('execution-logs');
        const fill = document.getElementById('progress-bar-fill');
        const statusText = document.getElementById('progress-status-text');
        const percentText = document.getElementById('progress-percent-text');
        const currentTestName = document.getElementById('current-test-name');
        const badge = document.getElementById('runner-status-badge');

        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/v1/executions/${executionId}`);
                const data = await res.json();

                const total = data.total_tests || 1;
                const completed = data.completed_tests || 0;
                const currentTest = data.current_test || 'Executing...';
                const currIdx = data.current_test_index || 1;
                const pct = data.progress_percent || 0;

                if (data.status === 'EXECUTING' || data.status === 'VALIDATING' || data.status === 'QUEUED') {
                    if (fill) fill.style.width = `${pct}%`;
                    if (percentText) percentText.textContent = `${pct}%`;
                    if (statusText) statusText.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-primary"></i> Executing Suite (${completed}/${total} Completed)`;
                    if (currentTestName) currentTestName.textContent = `Running Test ${currIdx} of ${total}: ${currentTest}`;

                    consoleBox.innerHTML = `
                        <div class="console-line text-primary" style="font-weight: 600; padding: 4px 8px; background: rgba(99, 102, 241, 0.15); border-radius: 4px;">
                            <i class="fa-solid fa-vial-circle-check text-primary"></i> [RUNNING TEST CASE ${currIdx}/${total}]: ${escapeHtml(currentTest)} (${pct}% Complete)
                        </div>
                        <div class="console-line text-muted mt-2">Execution ID: ${executionId} | Status: ${data.status}</div>
                        ${data.stdout ? `<pre class="console-line text-muted mt-3">${escapeHtml(data.stdout)}</pre>` : ''}
                    `;
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                } else {
                    // Terminal state reached (COMPLETED, PASSED, FAILED, etc.)
                    clearInterval(interval);
                    const isSuccess = (data.status === 'COMPLETED' || data.status === 'PASSED');
                    const colorClass = isSuccess ? 'text-success' : 'text-danger';

                    if (fill) {
                        fill.style.width = '100%';
                        fill.style.background = isSuccess 
                            ? 'linear-gradient(90deg, #10b981, #059669)' 
                            : 'linear-gradient(90deg, #ef4444, #dc2626)';
                    }
                    if (percentText) percentText.textContent = '100%';

                    if (badge) {
                        badge.className = isSuccess ? 'badge badge-pass' : 'badge badge-fail';
                        badge.textContent = isSuccess ? 'PASSED' : 'FAILED';
                    }

                    if (statusText) {
                        statusText.innerHTML = isSuccess 
                            ? `<i class="fa-solid fa-circle-check text-success"></i> Suite Run Complete (${total}/${total} Tests Finished)`
                            : `<i class="fa-solid fa-circle-xmark text-danger"></i> Suite Run Finished with Errors`;
                    }

                    if (currentTestName) {
                        currentTestName.textContent = isSuccess 
                            ? `All ${total} suite test cases finished successfully (${data.duration || 0}s)`
                            : `Suite finished with failures (${data.duration || 0}s)`;
                    }

                    let mcpLogHtml = '';
                    if (data.mcpResult && data.mcpResult.mcpToolLog) {
                        mcpLogHtml += `<div class="console-line text-info mt-4">--- MCP TOOL TRACE LOGS ---</div>`;
                        (data.mcpResult.mcpToolLog || []).forEach(log => {
                            mcpLogHtml += `<div class="console-line">Step ${log.step}: <code>${log.tool}</code> - ${log.status} ${log.testId ? `(Test: ${log.testId})` : ''} ${log.error ? `<span class="text-danger">(${log.error})</span>` : ''}</div>`;
                        });
                    }

                    consoleBox.innerHTML = `
                        <div class="console-line ${colorClass}" style="font-size: 1rem; font-weight: 700;">
                            [SUITE EXECUTION FINISHED] Status: ${data.status} | Total Tests: ${total} | Duration: ${data.duration || 0}s
                        </div>
                        <div class="console-line text-success mt-2">
                            <i class="fa-solid fa-file-invoice"></i> Extent Report successfully generated for entire suite run!
                        </div>
                        ${mcpLogHtml}
                        <div class="console-line mt-4">--- STDOUT LOGS ---</div>
                        <pre class="console-line text-muted">${escapeHtml(data.stdout || '')}</pre>
                        ${data.stderr ? `<div class="console-line text-danger mt-4">--- STDERR LOGS ---</div><pre class="console-line text-danger">${escapeHtml(data.stderr)}</pre>` : ''}
                    `;
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }
            } catch (err) {
                clearInterval(interval);
                consoleBox.innerHTML += `<div class="console-line text-danger">Error polling execution status: ${err.message}</div>`;
            }
        }, 1000);
    }

    // UI Helpers
    function updateValidationUI(val) {
        if (!val) return;
        if (val.status === 'PASS' || val.isValid) {
            validationBadge.className = 'badge badge-pass';
            validationBadge.textContent = 'VALID';
            validationSummary.innerHTML = '<i class="fa-solid fa-circle-check text-success"></i> Python syntax and framework symbols verified.';
        } else {
            validationBadge.className = 'badge badge-fail';
            validationBadge.textContent = 'ERROR';
            const errors = (val.errors || []).join('; ');
            validationSummary.innerHTML = `<i class="fa-solid fa-circle-xmark text-danger"></i> ${escapeHtml(errors)}`;
        }
    }

    function appendChatMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${role}`;
        msgDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i></div>
            <div class="msg-content">${text}</div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv.querySelector('.msg-content');
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
});

