/**
 * External APIs Main Component
 * 
 * Tab interface for GitHub, Slack, AWS, and Secrets
 */

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GitHubPanel } from './GitHubPanel';
import { SlackPanel } from './SlackPanel';
import { AWSPanel } from './AWSPanel';
import { SecretsManager } from './SecretsManager';

export function ExternalAPIs() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">External API Integration</h1>
        <p className="text-gray-600 mt-2">
          Manage integrations with GitHub, Slack, AWS, and secrets vault
        </p>
      </div>

      <Tabs defaultValue="github" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="github">🐙 GitHub</TabsTrigger>
          <TabsTrigger value="slack">💬 Slack</TabsTrigger>
          <TabsTrigger value="aws">☁️ AWS</TabsTrigger>
          <TabsTrigger value="secrets">🔐 Secrets</TabsTrigger>
        </TabsList>

        <TabsContent value="github">
          <GitHubPanel />
        </TabsContent>

        <TabsContent value="slack">
          <SlackPanel />
        </TabsContent>

        <TabsContent value="aws">
          <AWSPanel />
        </TabsContent>

        <TabsContent value="secrets">
          <SecretsManager />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export { GitHubPanel, SlackPanel, AWSPanel, SecretsManager };
