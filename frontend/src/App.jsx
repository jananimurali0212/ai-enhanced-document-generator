import React, { useState } from 'react';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { PromptForm } from './components/PromptForm';
import { DocumentEditor } from './components/DocumentEditor';
import { TEMPLATES } from './data/templates';

export function App() {
  const [currentStep, setCurrentStep] = useState(1); // 1: Dashboard, 2: Prompt, 3: Editor
  const [selectedTemplate, setSelectedTemplate] = useState(TEMPLATES[0]);
  const [files, setFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState(null);

  // Form parameters state
  const [formData, setFormData] = useState({
    topic: TEMPLATES[0].sampleTopic,
    purpose: TEMPLATES[0].samplePurpose,
    intendedAudience: TEMPLATES[0].sampleAudience,
    tone: TEMPLATES[0].defaultTone,
    desiredLength: TEMPLATES[0].defaultLength,
    additionalInstructions: "",
  });

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setFormData({
      topic: template.sampleTopic || "",
      purpose: template.samplePurpose || "",
      intendedAudience: template.sampleAudience || "",
      tone: template.defaultTone || "Professional",
      desiredLength: template.defaultLength || "Standard (~800-1,200 words)",
      additionalInstructions: "",
    });
    setCurrentStep(2);
  };

  const handleSelectCustom = () => {
    setSelectedTemplate(null);
    setFormData({
      topic: "",
      purpose: "",
      intendedAudience: "",
      tone: "Professional",
      desiredLength: "Standard (~800-1,200 words)",
      additionalInstructions: "",
    });
    setCurrentStep(2);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);

    const payload = {
      template_id: selectedTemplate ? selectedTemplate.id : 'custom',
      category: selectedTemplate ? selectedTemplate.category : 'General Document',
      topic: formData.topic,
      purpose: formData.purpose,
      intended_audience: formData.intendedAudience,
      tone: formData.tone,
      desired_length: formData.desiredLength,
      additional_instructions: formData.additionalInstructions,
      reference_files: files.map((f) => f.name),
    };

    try {
      // Attempt backend call first
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setGeneratedDoc(data);
      } else {
        throw new Error('Backend offline or responded with error');
      }
    } catch (err) {
      // Robust client-side mock fallback so Day 1 runs standalone out of the box
      await new Promise((resolve) => setTimeout(resolve, 800)); // simulate realistic generation feel
      
      const category = selectedTemplate ? selectedTemplate.category : "Custom Document";
      const fileMention = files.length > 0 
        ? `\n> **Grounding References:** Context injected from ${files.length} material(s): ${files.map(f => `\`${f.name}\``).join(', ')}.\n`
        : "";

      const mockMarkdown = `# ${formData.topic || "Untitled Document"}
*${category} Specification & Strategic Dossier*

**Document Status:** Ready for Review  
**Target Audience:** ${formData.intendedAudience || "General Stakeholders"}  
**Tone:** ${formData.tone} | **Target Scope:** ${formData.desiredLength}  
**Generated Date:** ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}  
${fileMention}
---

## 1. Executive Summary & Problem Framing
The overarching objective of this document is to **${formData.purpose || "provide clear operational direction"}**. 

In high-velocity environments, having structured documentation ensures alignment across cross-functional partners and eliminates ambiguity early in the project lifecycle.

## 2. Key Requirements & Scope
- **Direct Deliverable:** Comprehensive architectural roadmap and deployment guide.
- **Intended Readership:** Specifically tailored for **${formData.intendedAudience}** to drive immediate operational consensus.
- **Governance:** Aligned with ${formData.tone.toLowerCase()} communication standards.

## 3. High-Level Architecture & Workflow
\`\`\`
+-----------------------+       +-------------------------+       +------------------------+
|   Document Blueprint  |  -->  | AI Grounding & Parsing  |  -->  | Structured Editor Shell|
+-----------------------+       +-------------------------+       +------------------------+
\`\`\`

## 4. Key Performance Objectives
1. **Speed to Value:** Reduce draft iteration cycles from days to under 5 minutes.
2. **Context Adherence:** Seamless reference grounding with zero manual copy-pasting.
3. **Export Flexibility:** Export to GitHub Markdown, plain text, or downstream workflow tools.

## 5. Next Steps & Action Matrix
| Action Item | Assigned Stakeholder | Timeline | Status |
| :--- | :--- | :--- | :--- |
| Review initial Day 1 UI shell | Product & Engineering | Day 1 | Complete |
| Connect live LLM inference API | Backend Lead | Day 2 | Next Up |
| Ingest multi-file vector embeddings | AI/ML Engineer | Day 3 | Scheduled |

---
*Generated via DocuGen AI Day 1 Studio.*
`;

      setGeneratedDoc({
        id: `mock-${Date.now()}`,
        title: formData.topic || "Generated Document",
        category: category,
        tone: formData.tone,
        desired_length: formData.desiredLength,
        content: mockMarkdown,
        created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
    } finally {
      setIsGenerating(false);
      setCurrentStep(3);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header
        currentStep={currentStep}
        setStep={setCurrentStep}
        selectedTemplate={selectedTemplate}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentStep === 1 && (
          <Dashboard
            onSelectTemplate={handleSelectTemplate}
            onSelectCustom={handleSelectCustom}
          />
        )}

        {currentStep === 2 && (
          <PromptForm
            formData={formData}
            setFormData={setFormData}
            selectedTemplate={selectedTemplate}
            files={files}
            setFiles={setFiles}
            onGenerate={handleGenerate}
            onBack={() => setCurrentStep(1)}
            isGenerating={isGenerating}
          />
        )}

        {currentStep === 3 && (
          <DocumentEditor
            documentData={generatedDoc}
            onEditAnother={() => setCurrentStep(2)}
            onRegenerate={handleGenerate}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 DocuGen AI — Day 1 Architecture & UI Shell (React + Tailwind CSS & FastAPI)</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI Backend Ready</span>
            <span>•</span>
            <span>Client Mock Mode Active</span>
            <span>•</span>
            <span>Responsive Tailwind Layout</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
