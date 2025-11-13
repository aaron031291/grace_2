/**
 * Onboarding Walkthrough - First-time user guide
 * Explains Librarian pipeline, co-pilot, and key features
 */

import React, { useState } from 'react';
import { BookOpen, FolderTree, Sparkles, CheckCircle, ArrowRight, X } from 'lucide-react';

interface OnboardingWalkthroughProps {
  onComplete: () => void;
}

export function OnboardingWalkthrough({ onComplete }: OnboardingWalkthroughProps) {
  const [step, setStep] = useState(0);

  const steps = [
    {
      title: 'Welcome to Grace! 👋',
      icon: <Sparkles className="w-16 h-16 text-purple-400" />,
      content: (
        <div>
          <p className="text-gray-300 mb-4">
            Grace is your AI-powered knowledge platform that learns from your documents autonomously.
          </p>
          <p className="text-gray-300">
            The <span className="text-purple-400 font-semibold">Librarian</span> watches your files, 
            organizes them intelligently, and makes everything searchable.
          </p>
        </div>
      )
    },
    {
      title: 'How It Works 📚',
      icon: <BookOpen className="w-16 h-16 text-blue-400" />,
      content: (
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">1</div>
            <div>
              <div className="font-semibold text-white">Drop Files</div>
              <div className="text-sm text-gray-400">Just drag PDFs, docs, or books into folders</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">2</div>
            <div>
              <div className="font-semibold text-white">Librarian Processes</div>
              <div className="text-sm text-gray-400">Extracts text, creates chunks, generates embeddings</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">3</div>
            <div>
              <div className="font-semibold text-white">Verification & Trust</div>
              <div className="text-sm text-gray-400">Quality tests assign 0-100% trust scores</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">4</div>
            <div>
              <div className="font-semibold text-white">Query Anything</div>
              <div className="text-sm text-gray-400">Ask questions, get answers with citations</div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: 'Key Features 🚀',
      icon: <FolderTree className="w-16 h-16 text-green-400" />,
      content: (
        <div className="space-y-3">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-purple-500/30">
            <div className="font-semibold text-purple-400 mb-1">📚 Books Tab</div>
            <div className="text-sm text-gray-400">
              View your library, watch ingestion progress, quiz yourself with flashcards
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-blue-500/30">
            <div className="font-semibold text-blue-400 mb-1">🗂️ File Organizer</div>
            <div className="text-sm text-gray-400">
              AI-powered file sorting with <span className="font-bold">undo</span> for all operations
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-pink-500/30">
            <div className="font-semibold text-pink-400 mb-1">🤖 Co-pilot</div>
            <div className="text-sm text-gray-400">
              Always-visible assistant (bottom-right) for guidance and quick actions
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-yellow-500/30">
            <div className="font-semibold text-yellow-400 mb-1">⚡ Command Palette</div>
            <div className="text-sm text-gray-400">
              Press <kbd className="px-2 py-1 bg-gray-700 rounded">Ctrl+K</kbd> for quick commands
            </div>
          </div>
        </div>
      )
    },
    {
      title: 'Understanding Trust 🎯',
      icon: <CheckCircle className="w-16 h-16 text-yellow-400" />,
      content: (
        <div className="space-y-3">
          <p className="text-gray-300">
            Every document gets a <span className="font-bold text-yellow-400">trust score</span> (0-100%) based on quality tests:
          </p>
          <div className="bg-gray-800/50 rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-white font-medium">90-100%: HIGH</span>
              <span className="text-gray-400 text-sm">- Fully trusted, ready to use</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span className="text-white font-medium">70-90%: MEDIUM</span>
              <span className="text-gray-400 text-sm">- Usable with minor issues</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-white font-medium">&lt;70%: LOW</span>
              <span className="text-gray-400 text-sm">- Needs review before use</span>
            </div>
          </div>
          <p className="text-gray-400 text-sm mt-4">
            Low-trust files are automatically flagged. You can re-verify or manually approve them.
          </p>
        </div>
      )
    },
    {
      title: 'You\'re Ready! 🎉',
      icon: <CheckCircle className="w-16 h-16 text-green-400" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-300 text-lg">
            Grace is ready to start learning from your documents!
          </p>
          <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-6 border border-purple-500/30">
            <div className="font-semibold text-white mb-3">Try this first:</div>
            <ol className="space-y-2 text-sm text-gray-300">
              <li>1. Click the <span className="font-bold text-purple-400">📚 Books</span> tab above</li>
              <li>2. Drop a PDF into <code className="bg-gray-800 px-2 py-1 rounded">grace_training/documents/books/</code></li>
              <li>3. Watch the Librarian process it automatically</li>
              <li>4. Click the book → Press "Summarize" to query it</li>
            </ol>
          </div>
          <div className="text-center text-sm text-gray-400">
            Need help? Click the <span className="text-purple-400">Librarian Co-pilot</span> button (bottom-right) anytime!
          </div>
        </div>
      )
    }
  ];

  const currentStep = steps[step];

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-purple-500/30 rounded-2xl shadow-2xl max-w-2xl w-full">
        {/* Progress Bar */}
        <div className="h-2 bg-gray-800 rounded-t-2xl overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
            style={{ width: `${((step + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            {currentStep.icon}
          </div>

          {/* Title */}
          <h2 className="text-3xl font-bold text-center mb-6 text-white">
            {currentStep.title}
          </h2>

          {/* Content */}
          <div className="mb-8">
            {currentStep.content}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Step {step + 1} of {steps.length}
            </div>
            <div className="flex gap-3">
              {step < steps.length - 1 ? (
                <>
                  <button
                    onClick={onComplete}
                    className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                  >
                    Skip
                  </button>
                  <button
                    onClick={() => setStep(step + 1)}
                    className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-all flex items-center gap-2"
                  >
                    Next
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <button
                  onClick={onComplete}
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-all flex items-center gap-2"
                >
                  Get Started
                  <CheckCircle className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Close button */}
        <button
          onClick={onComplete}
          className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

export default OnboardingWalkthrough;
