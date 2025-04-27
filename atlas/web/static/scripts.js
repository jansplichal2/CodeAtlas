const serviceSelect = document.getElementById('serviceSelect');
const llmOptions = document.getElementById('llmOptions');
const llmProviderSelect = document.getElementById('llmProviderSelect');
const llmModelSelect = document.getElementById('llmModelSelect');
const documentation = document.getElementById('documentation');
const responseArea = document.getElementById('responseArea');

const docTexts = {
    relational: `**Relational DB**\n\nSchema:\n- Tables: Users, Projects, Commits\n- Example Query: SELECT * FROM Users WHERE id = 1;`,
    vector: `**Vector DB**\n\nEnter a semantic search query.\nExample: "Find code related to user authentication"`,
    graph: `**Graph DB**\n\nUsing Joern queries.\nExample: cpg.call.code(".*password.*")`,
    llm: `**LLM**\n\nEnter a prompt that will be processed by the selected LLM.`
};

const llmModels = {
    openai: ['ChatGPT 4o', 'ChatGPT 4o-mini'],
    anthropic: ['Claude 3.7 Sonnet']
};

function updateDocs() {
    const selected = serviceSelect.value;
    documentation.textContent = docTexts[selected] || '';
}

function toggleDocs() {
    documentation.style.display = documentation.style.display === 'none' ? 'block' : 'none';
}

serviceSelect.addEventListener('change', () => {
    if (serviceSelect.value === 'llm') {
        llmOptions.style.display = 'block';
    } else {
        llmOptions.style.display = 'none';
    }
    updateDocs();
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

document.getElementById('submitQuery').addEventListener('click', async () => {
    const payload = {
        service: serviceSelect.value,
        query: document.getElementById('queryInput').value,
    };
    if (payload.service === 'llm') {
        payload.llmProvider = llmProviderSelect.value;
        payload.llmModel = llmModelSelect.value;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Error ${response.status}`);
        const data = await response.json();
        responseArea.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseArea.textContent = `Request failed: ${error.message}`;
    }
});

// Initialize the first doc and LLM model list
updateDocs();
llmProviderSelect.dispatchEvent(new Event('change'));