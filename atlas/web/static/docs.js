const docTexts = {
  relational: `
<h3>Relational DB</h3>

<p><strong>Table:</strong> lines</p>

<table>
<thead>
<tr><th>Column</th><th>Type</th><th>Description</th></tr>
</thead>
<tbody>
<tr><td>id</td><td>INTEGER PRIMARY KEY</td><td>Unique row ID (auto-generated)</td></tr>
<tr><td>line_id</td><td>TEXT UNIQUE</td><td>Unique identifier for the source line</td></tr>
<tr><td>parent_type</td><td>TEXT</td><td>Parent block type (e.g. class, method), nullable</td></tr>
<tr><td>parent_method</td><td>TEXT</td><td>Parent method name, nullable</td></tr>
<tr><td>file_line_no</td><td>INTEGER</td><td>Line number in the source file</td></tr>
<tr><td>file_path</td><td>TEXT</td><td>Path to the source file</td></tr>
<tr><td>source</td><td>TEXT</td><td>Source code content of the line</td></tr>
<tr><td>created_at</td><td>TEXT</td><td>Timestamp when the record was created</td></tr>
</tbody>
</table>

<h4>Example Queries</h4>

<pre><code>SELECT * FROM lines
WHERE file_path = 'GenResourceService.java'
ORDER BY file_line_no;
</code></pre>

<pre><code>SELECT * FROM lines
WHERE parent_method = 'getResource'
ORDER BY file_line_no;
</code></pre>

<pre><code>SELECT * FROM lines
WHERE source LIKE '%password%';
</code></pre>`,

  vector: `
<h3>Vector DB</h3>

<p>Vector DB allows semantic search based on meaning rather than exact keywords.</p>

<p><strong>Input should be a natural language semantic query.</strong> Example:</p>

<pre><code>Find code related to user authentication</code></pre>

<p>Examples of useful queries:</p>

<ul>
<li>"Show me all lines related to password validation"</li>
<li>"Code snippets that check user permissions"</li>
<li>"Database connection handling"</li>
</ul>

<p>The system will return code chunks that semantically match the query.</p>
`,

  graph: `
<h3>Graph DB (Joern)</h3>

<p>Graph DB allows querying the source code as a graph (AST / CFG / etc).</p>

<p><strong>Input should be a valid Joern query (using Joern query language).</strong></p>

<p>Example queries:</p>

<pre><code>cpg.call.code(".*password.*")</code></pre>

<pre><code>cpg.method.name("getResource").ast.isCall</code></pre>

<p>Examples of tasks:</p>

<ul>
<li>Find all method calls with \"password\" in the code</li>
<li>Find methods calling other methods with specific names</li>
<li>Trace dataflow for sensitive variables</li>
</ul>

<p>Refer to Joern documentation for advanced queries.</p>
`,

  llm: `
<h3>LLM (Large Language Model)</h3>

<p>LLM can be used for semantic queries that require natural language understanding.</p>

<p><strong>Input should be a natural language query or prompt.</strong></p>

<p>Examples:</p>

<pre><code>Explain how user authentication is implemented in this codebase.</code></pre>

<pre><code>Find code examples related to password encryption.</code></pre>

<pre><code>List methods that handle sensitive data.</code></pre>

<p>The LLM will interpret the query and return context-aware answers.</p>
`
};
