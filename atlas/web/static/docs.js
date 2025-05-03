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
</code></pre>

<pre><code>SELECT * FROM lines
ORDER BY created_at DESC
LIMIT 10;
</code></pre>

<pre><code>SELECT * FROM lines
WHERE parent_method IS NULL
ORDER BY file_path, file_line_no;
</code></pre>
`
};
