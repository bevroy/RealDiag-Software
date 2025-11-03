const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static assets under /static from public/static
app.use('/static', express.static(path.join(__dirname, 'public', 'static')));

// Diagnostic page
app.get('/diagnostic', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'diagnostic.html'));
});

// root -> redirect to /diagnostic
app.get('/', (req, res) => res.redirect('/diagnostic'));

// simple health endpoint for the frontend
app.get('/health', (req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`Frontend server listening on port ${PORT}`);
});
