// Selection of services
const serviceSelect = document.getElementById('serviceSelect');
const llmOptions = document.getElementById('llmOptions');
const llmProviderSelect = document.getElementById('llmProviderSelect');
const llmModelSelect = document.getElementById('llmModelSelect');

// Documentation for different types of services
const documentation = document.getElementById('documentation');

// Handling of queries
const queryInput = document.getElementById('queryInput');
const submitButton = document.getElementById('submitQuery');
const responseArea = document.getElementById('responseArea');

const statusBar = {
    el: document.getElementById('statusBar'),
    setStatus(text) {
        this.el.textContent = text;
    }
};

const llmModels = {
    openai: ['ChatGPT 4o', 'ChatGPT 4o-mini'],
    anthropic: ['Claude 3.7 Sonnet']
};

function updateDocs() {
    const selected = serviceSelect.value;
    documentation.innerHTML = docTexts[selected] || '';
}

function clearResults() {
    responseArea.innerHTML = '';
}

function toggleDocs() {
    documentation.style.display = documentation.style.display === 'none' || documentation.style.display === "" ? 'block' : 'none';
}

serviceSelect.addEventListener('change', () => {
    if (serviceSelect.value === 'llm') {
        llmOptions.style.display = 'flex';
    } else {
        llmOptions.style.display = 'none';
    }
    updateDocs();
    clearResults();
    statusBar.setStatus('Ready.');
});

llmProviderSelect.addEventListener('change', () => {
    const provider = llmProviderSelect.value;
    llmModelSelect.innerHTML = '';
    llmModels[provider].forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        llmModelSelect.appendChild(option);
    });
});

submitButton.addEventListener('click', async () => {
    const payload = {
        service: serviceSelect.value,
        query: queryInput.value,
    };
    if (payload.service === 'llm') {
        payload.llmProvider = llmProviderSelect.value;
        payload.llmModel = llmModelSelect.value;
    }

    try {
        statusBar.setStatus(`Running query against ${payload.service}...`);
        showLoading();
        const start = performance.now();
        const response = await fetch('http://127.0.0.1:8000/api/v1/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            responseArea.textContent = `Request failed: ${response.status}`;
            statusBar.setStatus("Request failed.");
        } else {
            const elapsed = Math.round(performance.now() - start);
            statusBar.setStatus(`Query completed in ${elapsed} ms.`);
        }
        const data = await response.json();

        if (data.status === 'failure') {
            responseArea.textContent = data.result;
            return;
        }
        const result = data.result;

        if (data.service === "relational") {
            renderRelationalResult(result);
        } else if (data.service === "vector") {
            renderVectorResult(result);
        } else if (data.service === "graph") {
            renderGraphResult(result);
        } else if (data.service === "llm") {
            renderLLMResult(result);
        } else {
            responseArea.textContent = JSON.stringify(data, null, 2);
        }

    } catch (error) {
        responseArea.textContent = `Request failed: ${error.message}`;
    }
});

const renderRelationalResult = result => {
    responseArea.innerHTML = '';  // Clear previous

    if (!Array.isArray(result) || result.length === 0) {
        responseArea.textContent = "No results.";
        return;
    }

    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.marginTop = '1rem';

    // Create header
    const headerRow = document.createElement('tr');
    ['File Path', 'Line No.', 'Parent Type', 'Parent Method', 'Source'].forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.style.borderBottom = '1px solid #444';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Create rows
    result.forEach(item => {
        const row = document.createElement('tr');

        const filePath = item.file_path || '-';
        const lineNo = item.file_line_no !== null ? item.file_line_no : '-';
        const parentType = item.parent_type || '-';
        const parentMethod = item.parent_method || '-';
        const source = item.source || '';

        [filePath, lineNo, parentType, parentMethod, source].forEach(text => {
            const td = document.createElement('td');
            td.textContent = text;
            td.style.padding = '6px 8px';
            td.style.borderBottom = '1px solid #333';
            td.style.fontFamily = text === source ? 'monospace' : 'inherit';
            if (text === source) td.style.whiteSpace = 'pre'; // preserve spaces in source
            row.appendChild(td);
        });

        table.appendChild(row);
    });

    responseArea.appendChild(table);
}

function renderVectorResult(result) {
    const container = document.getElementById('responseArea');
    container.innerHTML = '';  // Clear previous

    if (!Array.isArray(result) || result.length === 0) {
        container.textContent = "No results.";
        return;
    }

    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.marginTop = '1rem';

    // Create header
    const headerRow = document.createElement('tr');
    ['File Path', 'Chunk No', 'Lines', 'Type', 'Name', 'Source'].forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.style.borderBottom = '1px solid #444';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Create rows
    result.forEach(data => {
        const row = document.createElement('tr');
        const item = data.payload;
        const filePath = item.file_path || '-';
        const chunkNo = item.chunk_no !== undefined ? item.chunk_no : '-';
        const lines = `${item.start_line ?? '-'} - ${item.end_line ?? '-'}`;
        const type = item.type || '-';
        const name = item.name || '-';
        const source = item.source || '';

        [filePath, chunkNo, lines, type, name].forEach(text => {
            const td = document.createElement('td');
            td.textContent = text;
            td.style.padding = '6px 8px';
            td.style.borderBottom = '1px solid #333';
            row.appendChild(td);
        });

        const sourceTd = document.createElement('td');
        const pre = document.createElement('pre');
        pre.textContent = source;
        pre.style.backgroundColor = '#1e1e1e';
        pre.style.padding = '6px';
        pre.style.borderRadius = '4px';
        pre.style.whiteSpace = 'pre-wrap';
        pre.style.overflowX = 'auto';
        pre.style.margin = '0';
        pre.style.fontFamily = 'monospace';

        sourceTd.appendChild(pre);
        sourceTd.style.verticalAlign = 'top';
        sourceTd.style.padding = '6px 8px';
        sourceTd.style.borderBottom = '1px solid #333';
        row.appendChild(sourceTd);

        table.appendChild(row);
    });

    container.appendChild(table);
}

function renderGraphResult(result) {
    const container = document.getElementById('responseArea');
    container.innerHTML = '';  // Clear previous


    const pre = document.createElement('pre');
    pre.style.backgroundColor = '#1e1e1e';
    pre.style.padding = '12px';
    pre.style.borderRadius = '6px';
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.overflowX = 'auto';
    pre.style.fontFamily = 'monospace';
    pre.style.color = '#c0c0c0';

    pre.textContent = result;

    container.appendChild(pre);
}

function renderLLMResult(result) {
    const container = document.getElementById('responseArea');
    container.innerHTML = '';  // Clear previous

    if (!result) {
        container.textContent = "No response.";
        return;
    }

    // Convert markdown to HTML using marked
    const html = marked.parse(result);

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    wrapper.style.backgroundColor = '#1e1e1e';
    wrapper.style.padding = '12px';
    wrapper.style.borderRadius = '6px';
    wrapper.style.color = '#c0c0c0';
    wrapper.style.fontFamily = 'sans-serif';
    wrapper.style.lineHeight = '1.6';
    wrapper.style.whiteSpace = 'pre-wrap';

    // Optional: style code blocks
    wrapper.querySelectorAll('code').forEach(codeBlock => {
        codeBlock.style.backgroundColor = '#2a2a2a';
        codeBlock.style.padding = '2px 4px';
        codeBlock.style.borderRadius = '3px';
        codeBlock.style.fontFamily = 'monospace';
    });

    container.appendChild(wrapper);
}

function showLoading() {
    const container = document.getElementById('responseArea');
    container.innerHTML = '';

    const loading = document.createElement('div');
    loading.textContent = 'Loading...';
    loading.style.color = '#888';
    loading.style.padding = '1rem';
    loading.style.fontStyle = 'italic';

    container.appendChild(loading);
}

// Initialize the first doc and LLM model list
updateDocs();
llmProviderSelect.dispatchEvent(new Event('change'));