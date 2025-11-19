/**
 * AWS Operations Panel
 * 
 * UI for S3, Lambda, EC2 operations
 */

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface S3Object {
  key: string;
  size: number;
  last_modified: string;
  etag: string;
}

interface LambdaFunction {
  name: string;
  runtime: string;
  handler: string;
  memory_size: number;
  timeout: number;
  code_size: number;
}

interface EC2Instance {
  instance_id: string;
  instance_type: string;
  state: string;
  launch_time: string;
  private_ip: string;
  public_ip?: string;
}

export function AWSPanel() {
  const [loading, setLoading] = useState(false);
  
  // S3 State
  const [s3Objects, setS3Objects] = useState<S3Object[]>([]);
  const [bucket, setBucket] = useState('');
  const [prefix, setPrefix] = useState('');
  
  // Lambda State
  const [functions, setFunctions] = useState<LambdaFunction[]>([]);
  
  // EC2 State
  const [instances, setInstances] = useState<EC2Instance[]>([]);
  
  // Cost tracking
  const [costSummary, setCostSummary] = useState<any>(null);

  const listS3Objects = async () => {
    if (!bucket) {
      alert('Please enter a bucket name');
      return;
    }

    setLoading(true);
    try {
      const url = `/api/external/aws/s3/list?bucket=${bucket}&prefix=${prefix}`;
      const response = await fetch(url);
      const data = await response.json();
      setS3Objects(data.objects || []);
    } catch (error) {
      alert(`Failed to list S3 objects: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const listLambdaFunctions = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/external/aws/lambda/functions');
      const data = await response.json();
      setFunctions(data.functions || []);
    } catch (error) {
      alert(`Failed to list Lambda functions: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const listEC2Instances = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/external/aws/ec2/instances');
      const data = await response.json();
      setInstances(data.instances || []);
    } catch (error) {
      alert(`Failed to list EC2 instances: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const getCostSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/external/aws/costs');
      const data = await response.json();
      setCostSummary(data);
    } catch (error) {
      alert(`Failed to get cost summary: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>☁️ AWS Integration</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="s3">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="s3">S3</TabsTrigger>
              <TabsTrigger value="lambda">Lambda</TabsTrigger>
              <TabsTrigger value="ec2">EC2</TabsTrigger>
              <TabsTrigger value="costs">Costs</TabsTrigger>
            </TabsList>

            {/* S3 Tab */}
            <TabsContent value="s3" className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Bucket name"
                  value={bucket}
                  onChange={(e) => setBucket(e.target.value)}
                />
                <Input
                  placeholder="Prefix (optional)"
                  value={prefix}
                  onChange={(e) => setPrefix(e.target.value)}
                />
                <Button onClick={listS3Objects} disabled={loading}>
                  {loading ? 'Loading...' : 'List Objects'}
                </Button>
              </div>

              {s3Objects.length > 0 && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {s3Objects.map((obj) => (
                    <div key={obj.key} className="p-3 border rounded">
                      <div className="font-semibold">{obj.key}</div>
                      <div className="flex gap-4 text-sm text-gray-600 mt-1">
                        <span>Size: {(obj.size / 1024 / 1024).toFixed(2)} MB</span>
                        <span>Modified: {new Date(obj.last_modified).toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Lambda Tab */}
            <TabsContent value="lambda" className="space-y-4">
              <Button onClick={listLambdaFunctions} disabled={loading}>
                {loading ? 'Loading...' : 'List Functions'}
              </Button>

              {functions.length > 0 && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {functions.map((func) => (
                    <div key={func.name} className="p-3 border rounded">
                      <div className="font-semibold">{func.name}</div>
                      <div className="flex gap-2 mt-2 flex-wrap">
                        <Badge variant="outline">Runtime: {func.runtime}</Badge>
                        <Badge variant="outline">Memory: {func.memory_size}MB</Badge>
                        <Badge variant="outline">Timeout: {func.timeout}s</Badge>
                        <Badge variant="outline">Size: {(func.code_size / 1024).toFixed(2)}KB</Badge>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Handler: {func.handler}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* EC2 Tab */}
            <TabsContent value="ec2" className="space-y-4">
              <Button onClick={listEC2Instances} disabled={loading}>
                {loading ? 'Loading...' : 'List Instances'}
              </Button>

              {instances.length > 0 && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {instances.map((instance) => (
                    <div key={instance.instance_id} className="p-3 border rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold">{instance.instance_id}</div>
                          <div className="text-sm text-gray-600 mt-1">
                            Type: {instance.instance_type}
                          </div>
                        </div>
                        <Badge
                          variant={instance.state === 'running' ? 'default' : 'secondary'}
                        >
                          {instance.state}
                        </Badge>
                      </div>
                      <div className="flex gap-4 text-sm text-gray-600 mt-2">
                        <span>Private: {instance.private_ip}</span>
                        {instance.public_ip && <span>Public: {instance.public_ip}</span>}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Launched: {new Date(instance.launch_time).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Costs Tab */}
            <TabsContent value="costs" className="space-y-4">
              <Button onClick={getCostSummary} disabled={loading}>
                {loading ? 'Loading...' : 'Get Cost Summary'}
              </Button>

              {costSummary && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                          ${costSummary.total_estimated_cost?.toFixed(4) || '0.0000'}
                        </div>
                        <div className="text-sm text-gray-600">Total Estimated Cost</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                          {costSummary.total_operations || 0}
                        </div>
                        <div className="text-sm text-gray-600">Total Operations</div>
                      </CardContent>
                    </Card>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Cost Breakdown</h3>
                    <div className="space-y-2">
                      {Object.entries(costSummary.tracker || {}).map(([key, value]: [string, any]) => (
                        <div key={key} className="p-3 border rounded">
                          <div className="flex justify-between">
                            <span className="font-medium">{key}</span>
                            <span>${value.total_cost?.toFixed(4) || '0.0000'}</span>
                          </div>
                          <div className="text-sm text-gray-600">
                            Operations: {value.count || 0}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
