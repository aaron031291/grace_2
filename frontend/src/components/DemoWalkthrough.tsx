import React, { useState, useEffect } from 'react';

interface WalkthroughStep {
  id: string;
  title: string;
  description: string;
  action?: string;
  component?: string;
  expected?: string;
}

const walkthroughSteps: WalkthroughStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Grace Memory Studio',
    description: 'Experience the complete autonomous knowledge ingestion and self-healing workflow.',
    action: 'Click Next to begin'
  },
  {
    id: 'upload_book',
    title: 'Step 1: Upload a Book',
    description: 'Drop a PDF or EPUB file into the ingestion area. Librarian will automatically detect and process it.',
    action: 'Upload a book file',
    component: 'file-drop',
    expected: 'File uploaded and ingestion started'
  },
  {
    id: 'librarian_processing',
    title: 'Step 2: Librarian Processing',
    description: 'Watch as Librarian analyzes the file, extracts metadata, and begins content processing.',
    expected: 'Ingestion progress shown, schema proposals generated'
  },
  {
    id: 'schema_review',
    title: 'Step 3: Schema Review',
    description: 'Review and approve the automatically generated schema for the book content.',
    action: 'Approve schema proposal',
    component: 'schema-review',
    expected: 'Schema approved, content ingestion continues'
  },
  {
    id: 'content_ingestion',
    title: 'Step 4: Content Ingestion',
    description: 'Librarian processes book chapters, creates knowledge chunks, and builds the memory index.',
    expected: 'Content fully ingested, trust score calculated'
  },
  {
    id: 'verification',
    title: 'Step 5: Verification & Trust',
    description: 'Verification kernel checks content integrity and calculates trust scores.',
    expected: 'Verification completed, trust score displayed'
  },
  {
    id: 'self_healing_demo',
    title: 'Step 6: Self-Healing Demo',
    description: 'Trigger a simulated failure to see self-healing in action.',
    action: 'Trigger mock failure',
    component: 'self-healing-trigger',
    expected: 'Self-healing playbook executes automatically'
  },
  {
    id: 'co_pilot_interaction',
    title: 'Step 7: Co-Pilot Interaction',
    description: 'Ask Grace questions about the ingested content using the co-pilot.',
    action: 'Ask: "Summarize the main themes"',
    component: 'co-pilot',
    expected: 'Co-pilot provides intelligent summary'
  },
  {
    id: 'knowledge_quiz',
    title: 'Step 8: Knowledge Assessment',
    description: 'Test your understanding with AI-generated flashcards and quizzes.',
    action: 'Take knowledge quiz',
    component: 'flashcards',
    expected: 'Quiz completed with performance feedback'
  },
  {
    id: 'complete',
    title: 'Demo Complete!',
    description: 'You\'ve experienced the full Grace autonomous knowledge workflow. The system can now ingest, heal, and teach itself.',
    action: 'Explore more features or start over'
  }
];

export default function DemoWalkthrough() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const step = walkthroughSteps[currentStep];

  const nextStep = () => {
    if (currentStep < walkthroughSteps.length - 1) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const startDemo = () => {
    setIsActive(true);
    setCurrentStep(0);
    setCompletedSteps(new Set());
  };

  const endDemo = () => {
    setIsActive(false);
    setCurrentStep(0);
    setCompletedSteps(new Set());
  };

  const triggerDemoAction = async (action: string) => {
    switch (action) {
      case 'upload_book':
        // Simulate file upload
        alert('Demo: Simulating book upload...');
        setTimeout(() => nextStep(), 2000);
        break;
      case 'approve_schema':
        // Simulate schema approval
        alert('Demo: Simulating schema approval...');
        setTimeout(() => nextStep(), 1500);
        break;
      case 'trigger_failure':
        // Trigger self-healing demo
        await fetch('/api/self-healing/trigger-manual', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            component: 'demo_failure',
            error_details: { demo: true, message: 'Simulated ingestion failure' }
          })
        });
        alert('Demo: Self-healing triggered!');
        setTimeout(() => nextStep(), 3000);
        break;
      case 'ask_question':
        // Simulate co-pilot interaction
        alert('Demo: Co-pilot would respond here...');
        setTimeout(() => nextStep(), 2000);
        break;
      case 'take_quiz':
        // Simulate quiz
        alert('Demo: Quiz completed! Score: 85%');
        setTimeout(() => nextStep(), 2000);
        break;
      default:
        nextStep();
    }
  };

  if (!isActive) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '12px', border: '1px solid #333', textAlign: 'center', maxWidth: '600px' }}>
          <h1 style={{ color: '#00d4ff', marginBottom: '1rem', fontSize: '2rem' }}>
            🚀 Grace Demo Walkthrough
          </h1>
          <p style={{ color: '#ccc', marginBottom: '2rem', lineHeight: '1.6' }}>
            Experience the complete autonomous knowledge workflow: from book upload through
            ingestion, self-healing, and intelligent quizzing. See how Grace learns, heals itself,
            and becomes more trustworthy over time.
          </p>
          <button
            onClick={startDemo}
            style={{
              background: '#00d4ff',
              color: '#000',
              border: 'none',
              padding: '1rem 2rem',
              borderRadius: '8px',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              marginRight: '1rem'
            }}
          >
            Start Demo
          </button>
          <button
            onClick={() => window.history.back()}
            style={{
              background: '#333',
              color: '#fff',
              border: 'none',
              padding: '1rem 2rem',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Back to App
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      {/* Progress Bar */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <span style={{ color: '#888', marginRight: '1rem' }}>
            Step {currentStep + 1} of {walkthroughSteps.length}
          </span>
          <div style={{ flex: 1, height: '4px', background: '#333', borderRadius: '2px' }}>
            <div
              style={{
                height: '100%',
                background: '#00d4ff',
                borderRadius: '2px',
                width: `${((currentStep + 1) / walkthroughSteps.length) * 100}%`,
                transition: 'width 0.3s ease'
              }}
            />
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem', fontSize: '1.5rem' }}>
          {step.title}
        </h2>
        <p style={{ color: '#ccc', marginBottom: '2rem', lineHeight: '1.6', fontSize: '1.1rem' }}>
          {step.description}
        </p>

        {step.expected && (
          <div style={{ background: '#2a2a3e', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
            <strong style={{ color: '#4ade80' }}>Expected:</strong> {step.expected}
          </div>
        )}

        {/* Demo Actions */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {step.action && (
            <button
              onClick={() => triggerDemoAction(step.id)}
              style={{
                background: '#00d4ff',
                color: '#000',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              {step.action}
            </button>
          )}

          {currentStep > 0 && (
            <button
              onClick={prevStep}
              style={{
                background: '#333',
                color: '#fff',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Previous
            </button>
          )}

          <button
            onClick={nextStep}
            disabled={currentStep === walkthroughSteps.length - 1}
            style={{
              background: currentStep === walkthroughSteps.length - 1 ? '#333' : '#4ade80',
              color: '#fff',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              cursor: currentStep === walkthroughSteps.length - 1 ? 'not-allowed' : 'pointer',
              opacity: currentStep === walkthroughSteps.length - 1 ? 0.5 : 1
            }}
          >
            {currentStep === walkthroughSteps.length - 1 ? 'Complete' : 'Next'}
          </button>

          <button
            onClick={endDemo}
            style={{
              background: '#ff6b6b',
              color: '#fff',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            End Demo
          </button>
        </div>
      </div>

      {/* Step Indicators */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {walkthroughSteps.map((_, idx) => (
          <div
            key={idx}
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: completedSteps.has(idx) ? '#4ade80' :
                         idx === currentStep ? '#00d4ff' : '#333',
              transition: 'background 0.3s ease'
            }}
          />
        ))}
      </div>
    </div>
  );
}