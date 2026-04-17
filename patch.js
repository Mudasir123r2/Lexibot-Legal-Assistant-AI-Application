const fs = require('fs');
const path = 'client/src/pages/Dashboard/CasesDashboard.jsx';
let text = fs.readFileSync(path, 'utf8');

const startIdx = text.indexOf('  const handleSubmit = async (e) => {');
const endIdx = text.indexOf('      closeDrawer();', startIdx);

if (startIdx !== -1 && endIdx !== -1) {
    const newBlock = `  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      let payload = { ...formData };
      if (typeof payload.tags === 'string') {
        payload.tags = payload.tags.split(',').map(t => t.trim()).filter(t => t);
      }
      if (!payload.filingDate) delete payload.filingDate;
      if (!payload.hearingDate) delete payload.hearingDate;
      if (!payload.deadline) delete payload.deadline;

      if (editingCase) {
        await api.put(\`/cases/\${editingCase._id}\`, payload);
      } else {
        await api.post("/cases", payload);
      }
`;
    fs.writeFileSync(path, text.substring(0, startIdx) + newBlock + text.substring(endIdx), 'utf8');
    console.log("Patched Date Validation");
} else {
    console.log("Could not find block.", startIdx, endIdx);
}
